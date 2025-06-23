from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    VUELOS = "vuelos"
    ALQUILERAUTOS = "alquiler_autos"
    HOTEL = "hotel"
    ALLINCLUSIVE = "all_inclusive"

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del producto")
    description: str = Field(..., min_length=1, max_length=1000, description="Descripción del producto")
    price: float = Field(..., gt=0, description="Precio del producto debe ser mayor que 0")
    category: CategoryEnum = Field(..., description="Categoría del producto")
    stock: int = Field(..., ge=0, description="Cantidad disponible del producto")
    image_url: Optional[str] = Field(None, description="URL de la imagen del producto")
    sku: Optional[str] = Field(None, max_length=50, description="Código SKU del producto")

class ProductCreate(ProductBase):
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor que 0')
        return round(v, 2)  # Redondear a 2 decimales

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[CategoryEnum] = None
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El precio debe ser mayor que 0')
        return round(v, 2) if v is not None else v

class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0, description="Nueva cantidad de stock")

class Product(ProductBase):
    id: int
    is_active: bool = Field(default=True, description="Indica si el producto está activo")
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True