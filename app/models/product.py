from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer)  
    is_active = Column(Boolean, default=True)  
    category = Column(String(50), index=True)  # Cambiado a String para coincidir con el Enum
    sku = Column(String(50), unique=True, nullable=True)  # SKU único y opcional
    stock = Column(Integer, default=0)  # Stock con valor por defecto 0
    image_url = Column(String(255), nullable=True)  # URL de la imagen, opcional

    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=True)

    sale_items = relationship("SaleItem", back_populates="product")