from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del producto")
    description: str = Field(..., min_length=1, max_length=1000, description="Descripción del producto")
    price: float = Field(..., gt=0, description="Precio del producto debe ser mayor que 0")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    is_active: bool = Field(default=True, description="Indica si el producto está activo")  