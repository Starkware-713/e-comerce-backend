from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import User
from app.models.product import Product

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Integer, nullable=False)  # Precio al momento de la compra
    
    product = relationship("Product")
    order = relationship("Order", back_populates="items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    status = Column(String, default="pending")  # pending, created, paid, processing, shipped, delivered, cancelled
    total_amount = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)