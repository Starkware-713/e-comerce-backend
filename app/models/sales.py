from sqlalchemy import Column, Integer, String, Boolean
from app.models import Base
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer, default=1)
    total_price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)  # Indicates if the sale is active
    client_id = Column(Integer, index=True)  