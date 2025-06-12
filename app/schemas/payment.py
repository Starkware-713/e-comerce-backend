from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    TRANSFER = "transfer"
    MERCADO_PAGO = "mercado_pago"

class PaymentRequest(BaseModel):
    order_id: int
    payment_method: PaymentMethod
    customer_id: int

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    status: PaymentStatus
    transaction_id: Optional[str]
    payment_date: datetime
    invoice_number: Optional[int]
    
    class Config:
        from_attributes = True
