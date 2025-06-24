from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from app.models import Base  # Unifica la importación de Base

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_percent = Column(Float)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    max_uses = Column(Integer)
    current_uses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)