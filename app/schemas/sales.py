from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from .product import Product
from .user import User

class SaleItemBase(BaseModel):
    product: Product
    quantity: int = Field(..., gt=0)
    unit_price: int = Field(..., gt=0)

class SaleItem(SaleItemBase):
    id: int
    sale_id: int

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    total_amount: int = Field(..., gt=0)
    status: str = Field(..., description="Estado de la venta: pending, completed, cancelled")

class Sale(SaleBase):
    id: int
    order_number: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    user: User
    items: List[SaleItem]

    class Config:
        from_attributes = True
