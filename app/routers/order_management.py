from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.orders import Order as OrderModel, OrderItem
from app.models.order_history import OrderHistory, OrderHistoryItem
from app.schemas import order as order_schemas
from app.schemas import order_history as history_schemas
from app.utils import get_current_user, check_rol
from app.models.user import User

router = APIRouter(
    prefix="/orders/management",
    tags=["order management"]
)

@router.get("/pending", response_model=list[order_schemas.OrderDetail])
async def get_pending_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    """Ver pedidos pendientes"""
    try:
        orders = (
            db.query(OrderModel)
            .filter(OrderModel.status.in_(["pending", "confirmed", "paid", "processing", "shipped"]))
            .options(
                joinedload(OrderModel.items).joinedload(OrderItem.product),
                joinedload(OrderModel.user)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return orders
    except Exception as e:
        print(f"Error obteniendo órdenes pendientes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=list[order_schemas.OrderDetail])
async def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    """Ver todas las órdenes"""
    try:
        query = db.query(OrderModel)
        if status:
            query = query.filter(OrderModel.status == status)
        
        orders = (
            query.options(
                joinedload(OrderModel.items).joinedload(OrderItem.product),
                joinedload(OrderModel.user)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return orders
    except Exception as e:
        print(f"Error obteniendo órdenes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/{order_id}/deliver", response_model=history_schemas.OrderHistory)
async def mark_as_delivered(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    """Marcar pedido como entregado"""
    try:
        order = (
            db.query(OrderModel)
            .filter(OrderModel.id == order_id)
            .options(
                joinedload(OrderModel.items).joinedload(OrderItem.product),
                joinedload(OrderModel.user)
            )
            .first()
        )

        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        if order.status not in ["processing", "shipped"]:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden entregar pedidos en estado processing o shipped"
            )
        
        # Crear entrada en el historial
        history_entry = OrderHistory(
            order_number=order.order_number,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status="delivered",
            created_at=order.created_at,
            delivered_at=datetime.utcnow()
        )
        db.add(history_entry)
        db.flush()  # Para obtener el ID
        
        # Mover items al historial
        for item in order.items:
            history_item = OrderHistoryItem(
                order_history_id=history_entry.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(history_item)
        
        # Marcar orden original como entregada y moverla al historial
        order.status = "delivered"
        
        db.commit()
        db.refresh(history_entry)
        return history_entry
        
    except Exception as e:
        db.rollback()
        print(f"Error marcando orden como entregada: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/{order_id}/cancel", response_model=history_schemas.OrderHistory)
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    """Anular pedido"""
    try:
        order = (
            db.query(OrderModel)
            .filter(OrderModel.id == order_id)
            .options(
                joinedload(OrderModel.items).joinedload(OrderItem.product),
                joinedload(OrderModel.user)
            )
            .first()
        )
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        if order.status not in ["pending", "confirmed", "paid"]:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden anular pedidos en estado pending, confirmed o paid"
            )
        
        # Crear entrada en el historial
        history_entry = OrderHistory(
            order_number=order.order_number,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status="cancelled",
            created_at=order.created_at,
            cancelled_at=datetime.utcnow()
        )
        db.add(history_entry)
        db.flush()  # Para obtener el ID
        
        # Mover items al historial y restaurar stock
        for item in order.items:
            history_item = OrderHistoryItem(
                order_history_id=history_entry.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(history_item)
            
            # Restaurar stock
            product = item.product
            product.stock += item.quantity
        
        # Marcar orden original como cancelada
        order.status = "cancelled"
        
        db.commit()
        db.refresh(history_entry)
        return history_entry
        
    except Exception as e:
        db.rollback()
        print(f"Error cancelando orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")