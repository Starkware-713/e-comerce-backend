from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional, List
from app.database import get_db
from app.models import cart as cart_models
from app.models.orders import Order, OrderItem
from app.schemas import order as schemas
from app.utils import get_current_user, check_rol
from app.utils.order import generate_order_number, calculate_order_total 
from app.utils.mail_sender import send_order_confirmation
from app.models.user import User

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("/", response_model=List[schemas.OrderSummary])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort: Optional[str] = Query(None, enum=["date_asc", "date_desc", "total_asc", "total_desc"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        query = db.query(Order).filter(Order.user_id == current_user.id)
        
        if status:
            query = query.filter(Order.status == status)
            
        if start_date:
            query = query.filter(Order.created_at >= start_date)
            
        if end_date:
            query = query.filter(Order.created_at <= end_date)
            
        if sort:
            if sort == "date_asc":
                query = query.order_by(Order.created_at)
            elif sort == "date_desc":
                query = query.order_by(desc(Order.created_at))
            elif sort == "total_asc":
                query = query.order_by(Order.total_amount)
            elif sort == "total_desc":
                query = query.order_by(desc(Order.total_amount))
        else:
            query = query.order_by(desc(Order.created_at))  # Default newest first
            
        orders = query.offset(skip).limit(limit).all()
        
        if not orders:
            return JSONResponse(
                status_code=404,
                content={"detail": "No hay órdenes para el usuario"}
            )
            
        return orders
        
    except Exception as e:
        print(f"Error obteniendo órdenes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{order_id}", response_model=schemas.OrderDetail)
async def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).options(
            joinedload(Order.items).joinedload(OrderItem.product)
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
            
        return order
        
    except Exception as e:
        print(f"Error obteniendo detalles de la orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/create", response_model=schemas.OrderDetail)
async def create_order(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. Obtener el carrito y validar
        cart = db.query(cart_models.Cart).filter(
            cart_models.Cart.id == cart_id,
            cart_models.Cart.user_id == current_user.id,
            cart_models.Cart.status == "active"
        ).options(
            joinedload(cart_models.Cart.items).joinedload(cart_models.CartItem.product)
        ).first()
        
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado o no está activo")
        
        if not cart.items:
            raise HTTPException(status_code=400, detail="El carrito está vacío")

        # 2. Validar stock disponible
        for item in cart.items:
            if item.quantity > item.product.stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para el producto: {item.product.name}"
                )

        # 3. Crear la orden
        total_amount = calculate_order_total(cart.items)
        order_number = generate_order_number()
        
        new_order = Order(
            order_number=order_number,
            user_id=current_user.id,
            status="pending",
            total_amount=total_amount,
            shipping_address=current_user.default_address,  # Asumiendo que existe este campo
            created_at=datetime.utcnow()
        )
        db.add(new_order)
        db.flush()  # Para obtener el ID de la orden

        # 4. Crear items de la orden y actualizar stock
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                subtotal=cart_item.quantity * cart_item.product.price
            )
            db.add(order_item)
            
            # Actualizar stock
            cart_item.product.stock -= cart_item.quantity

        # 5. Marcar carrito como procesado
        cart.status = "processed"
        
        db.commit()
        
        # 6. Enviar confirmación por email
        await send_order_confirmation(
            to_email=current_user.email,
            order_number=order_number,
            total_amount=total_amount,
            items=cart.items
        )
        
        # 7. Retornar orden creada con todos sus detalles
        return await get_order_detail(new_order.id, db, current_user)
        
    except Exception as e:
        db.rollback()
        print(f"Error creando la orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/stats/summary", response_model=schemas.OrderStats)
async def get_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        total_orders = db.query(Order).filter(Order.user_id == current_user.id).count()
        pending_orders = db.query(Order).filter(
            Order.user_id == current_user.id,
            Order.status == "pending"
        ).count()
        completed_orders = db.query(Order).filter(
            Order.user_id == current_user.id,
            Order.status == "completed"
        ).count()
        total_spent = db.query(func.sum(Order.total_amount)).filter(
            Order.user_id == current_user.id,
            Order.status == "completed"
        ).scalar() or 0.0
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "total_spent": total_spent
        }
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

