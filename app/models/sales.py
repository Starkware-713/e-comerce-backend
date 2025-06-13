from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.product import Product
from app.models.user import User
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    TRANSFER = "transfer"
    MERCADO_PAGO = "mercado_pago"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True)
    payment_date = Column(DateTime, default=datetime.utcnow)
    customer_id = Column(Integer, ForeignKey("users.id"))
    
    order = relationship("Order", back_populates="payments")
    customer = relationship("User")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Integer, nullable=False)
    
    product = relationship("Product")
    sale = relationship("Sale", back_populates="items")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    invoice_number = Column(Integer, unique=True, index=True)
    order_number = Column(String, unique=True, index=True)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    status = Column(String, default="pending")  # pending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    items = relationship("SaleItem", back_populates="sale")
    order = relationship("Order")
    payment = relationship("Payment")
    user = relationship("User")