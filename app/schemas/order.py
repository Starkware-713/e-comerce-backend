from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
from app.schemas.product import Product
from app.schemas.user import User

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class OrderItemBase(BaseModel):
    product: Product
    quantity: int = Field(..., ge=1, description="Cantidad del producto en la orden")
    unit_price: float = Field(..., gt=0, description="Precio unitario del producto al momento de la compra")
    subtotal: float = Field(..., gt=0, description="Subtotal del item (quantity * unit_price)")

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product_id: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    cart_id: int = Field(..., description="ID del carrito a convertir en orden")
    shipping_address: Optional[str] = Field(None, description="Dirección de envío para esta orden específica")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales para la orden")

class OrderSummary(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    total_amount: float
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True

class OrderDetail(BaseModel):
    id: int
    order_number: str
    user: User
    items: List[OrderItem]
    status: OrderStatus
    total_amount: float
    shipping_address: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    payment_status: Optional[str]
    tracking_number: Optional[str]
    estimated_delivery: Optional[datetime]

    class Config:
        from_attributes = True

class OrderStats(BaseModel):
    total_orders: int = Field(..., description="Total número de órdenes")
    pending_orders: int = Field(..., description="Número de órdenes pendientes")
    completed_orders: int = Field(..., description="Número de órdenes completadas")
    total_spent: float = Field(..., description="Total gastado en todas las órdenes completadas")

    @validator('total_spent')
    def round_total_spent(cls, v):
        return round(v, 2)