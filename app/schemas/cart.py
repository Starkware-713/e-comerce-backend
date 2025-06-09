from pydantic import BaseModel,  Field
from typing import List
from app.schemas.product import Product
from app.schemas.user import User
class CartItem(BaseModel):
    product: Product
    quantity: int = Field(..., ge=1, description="Cantidad del producto en el carrito")

class CartCreate(BaseModel):
    user_id: int
    items: List[CartItem]

class CartUpdate(BaseModel):
    items: List[CartItem]

class Cart(BaseModel):
    id: int
    user: User
    items: List[CartItem]