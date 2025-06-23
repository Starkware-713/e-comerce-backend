from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)  
    is_active = Column(Boolean, default=True)  
    category = Column(Integer, index=True) 
    sku = Column(String(50), unique=True, nullable=True)  # SKU único y opcional
    stock = Column(Integer, default=0)  # Stock con valor por defecto 0
    image_url = Column(String(255), nullable=True)  # URL de la imagen, opcional

    sale_items = relationship("SaleItem", back_populates="product")