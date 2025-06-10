from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from app.schemas.product import Product
from app.schemas.user import User

class OrderItemBase(BaseModel):
    product: Product
    quantity: int = Field(..., ge=1, description="Cantidad del producto en la orden")
    unit_price: int = Field(..., gt=0, description="Precio unitario del producto al momento de la compra")

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product_id: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    cart_id: int = Field(..., description="ID del carrito a convertir en orden")

class Order(BaseModel):
    id: int
    order_number: str
    user: User
    items: List[OrderItem]
    status: str = Field(..., description="Estado de la orden: pending, created, paid, processing, shipped, delivered, cancelled")
    total_amount: int
    created_at: datetime

    class Config:
        from_attributes = True