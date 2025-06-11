from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.orders import Order as OrderModel
from app.models.order_history import OrderHistory, OrderHistoryItem
from app.schemas import order as order_schemas
from app.schemas import order_history as history_schemas
from app.utils import get_current_user, check_rol
from app.models.user import User

router = APIRouter(
    prefix="/orders/management",
    tags=["order management"]
)

@router.get("/pending", response_model=list[order_schemas.Order])
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
            .filter(OrderModel.status.in_(["pending", "created", "paid", "processing", "shipped"]))
            .options(
                joinedload(OrderModel.items).joinedload(OrderModel.product),
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

@router.post("/{order_id}/deliver", response_model=history_schemas.OrderHistory)
async def mark_as_delivered(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    """Marcar pedido como entregado"""
    try:
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        if order.status not in ["shipped", "processing"]:
            raise HTTPException(
                status_code=400,
                detail="Solo se pueden marcar como entregados los pedidos en estado 'shipped' o 'processing'"
            )
        
        # Crear registro en el historial
        history_order = OrderHistory(
            order_number=order.order_number,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status="delivered",
            created_at=order.created_at,
            delivered_at=datetime.utcnow()
        )
        db.add(history_order)
        db.flush()
        
        # Copiar items al historial
        for item in order.items:
            history_item = OrderHistoryItem(
                order_history_id=history_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(history_item)
        
        # Eliminar orden original
        db.delete(order)
        db.commit()
        db.refresh(history_order)
        
        return history_order
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
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        if order.status in ["delivered", "cancelled"]:
            raise HTTPException(
                status_code=400,
                detail="No se puede cancelar un pedido que ya está entregado o cancelado"
            )
        
        # Crear registro en el historial
        history_order = OrderHistory(
            order_number=order.order_number,
            user_id=order.user_id,
            total_amount=order.total_amount,
            status="cancelled",
            created_at=order.created_at,
            cancelled_at=datetime.utcnow()
        )
        db.add(history_order)
        db.flush()
        
        # Copiar items al historial
        for item in order.items:
            history_item = OrderHistoryItem(
                order_history_id=history_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(history_item)
        
        # Eliminar orden original
        db.delete(order)
        db.commit()
        db.refresh(history_order)
        
        return history_order
    except Exception as e:
        db.rollback()
        print(f"Error cancelando la orden: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/history", response_model=list[history_schemas.OrderHistory])
async def get_order_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    """Obtener historial de pedidos"""
    try:
        history = (
            db.query(OrderHistory)
            .options(
                joinedload(OrderHistory.items).joinedload(OrderHistoryItem.product),
                joinedload(OrderHistory.user)
            )
            .order_by(OrderHistory.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return history
    except Exception as e:
        print(f"Error obteniendo historial de órdenes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")