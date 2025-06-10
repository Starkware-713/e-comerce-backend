from pydantic import BaseModel, Field
from typing import List
from app.schemas.product import Product
from app.schemas.user import User

class CartItemBase(BaseModel):
    quantity: int = Field(..., ge=1, description="Cantidad del producto en el carrito")

class CartItemCreate(CartItemBase):
    product: Product

class CartItem(CartItemBase):
    id: int
    cart_id: int
    product: Product

    class Config:
        from_attributes = True

class CartCreate(BaseModel):
    user_id: int
    items: List[CartItemCreate]

class CartUpdate(BaseModel):
    items: List[CartItem]

class Cart(BaseModel):
    id: int
    user: User
    items: List[CartItem]