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
    
    sale_items = relationship("SaleItem", back_populates="product")