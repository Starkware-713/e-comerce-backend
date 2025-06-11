from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.user import User
from app.schemas.product import Product

class OrderHistoryItemBase(BaseModel):
    product: Product
    quantity: int
    unit_price: int

class OrderHistoryItem(OrderHistoryItemBase):
    id: int
    order_history_id: int

    class Config:
        from_attributes = True

class OrderHistory(BaseModel):
    id: int
    order_number: str
    user: User
    items: List[OrderHistoryItem]
    status: str = Field(..., description="Estado de la orden: entregada, cancelada")
    total_amount: int
    created_at: datetime
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True