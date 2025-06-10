from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import cart as cart_models
from app.models.orders import Order as order_models
from app.models.orders import OrderItem
from app.schemas import order as schemas
from app.utils import get_current_user
from app.utils.order import generate_order_number, calculate_order_total 
from app.utils.mail_sender import send_order_confirmation
from app.models.user import User

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

# Creación de una orden de compra
@router.post("/create", response_model=schemas.Order)
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

        # 2. Crear la orden
        order_number = generate_order_number()
        db_order = order_models.Order(
            order_number=order_number,
            user_id=current_user.id,
            status="pending"
        )
        db.add(db_order)
        db.flush()  # Para obtener el ID de la orden

        # 3. Crear los items de la orden
        total_amount = 0
        for cart_item in cart.items:
            order_item = order_models.OrderItem(
                order_id=db_order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            total_amount += cart_item.quantity * cart_item.product.price
            db.add(order_item)        # 4. Actualizar el total y el estado de la orden
        db_order.total_amount = total_amount
        db_order.status = "created"

        # 5. Limpiar el carrito
        cart.status = "completed"
        for item in cart.items:
            db.delete(item)

        db.commit()
        db.refresh(db_order)

        # 6. Enviar correo de confirmación
        order_items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == db_order.id)
            .options(joinedload(OrderItem.product))
            .all()
        )
        
        send_order_confirmation(
            to_email=current_user.email,
            order_number=db_order.order_number,
            total_amount=db_order.total_amount,
            items=order_items
        )

        return db_order

    except Exception as e:
        db.rollback()
        print(f"Error creando la orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=list[schemas.Order])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todas las órdenes del usuario actual"""
    try:
        orders = (
            db.query(order_models.Order)
            .filter(order_models.Order.user_id == current_user.id)
            .options(
                joinedload(order_models.Order.items).joinedload(order_models.OrderItem.product)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return orders
    except Exception as e:
        print(f"Error obteniendo órdenes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{order_id}", response_model=schemas.Order)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el detalle de una orden específica"""
    try:
        order = (
            db.query(order_models.Order)
            .filter(
                order_models.Order.id == order_id,
                order_models.Order.user_id == current_user.id
            )
            .options(
                joinedload(order_models.Order.items).joinedload(order_models.OrderItem.product)
            )
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return order
    except Exception as e:
        print(f"Error obteniendo la orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/{order_id}/status", response_model=schemas.Order)
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza el estado de una orden"""
    valid_statuses = ["pending", "created", "paid", "processing", "shipped", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}")
    
    try:
        order = (
            db.query(order_models.Order)
            .filter(
                order_models.Order.id == order_id,
                order_models.Order.user_id == current_user.id
            )
            .first()
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
            
        order.status = status
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        print(f"Error actualizando el estado de la orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

