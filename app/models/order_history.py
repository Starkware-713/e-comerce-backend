from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models import Base
from app.models.user import User
from app.models.product import Product

class OrderHistory(Base):
    __tablename__ = "order_history"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Integer, default=0)
    status = Column(String)  # delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    user = relationship("User")

class OrderHistoryItem(Base):
    __tablename__ = "order_history_items"
    id = Column(Integer, primary_key=True, index=True)
    order_history_id = Column(Integer, ForeignKey("order_history.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Integer, nullable=False)
    
    product = relationship("Product")
    order_history = relationship("OrderHistory", backref="items")