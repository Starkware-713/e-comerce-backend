from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import PaymentRequest, PaymentResponse, PaymentStatus
from app.models.sales import Payment, Sale
from app.models.orders import Order
from app.utils.mail_sender import send_payment_confirmation
from datetime import datetime
import random

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

def generate_invoice_number(db: Session) -> int:
    """Generate a unique invoice number"""
    last_sale = db.query(Sale).order_by(Sale.invoice_number.desc()).first()
    if last_sale:
        return last_sale.invoice_number + 1
    return 1000  # Start from 1000

def calculate_tax(amount: float) -> float:
    """Calculate tax amount (IVA 21%)"""
    return amount * 0.21

@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Verify order exists and belongs to customer
    order = db.query(Order).filter(
        Order.id == payment_data.order_id,
        Order.user_id == payment_data.customer_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada o no pertenece al cliente"
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="La orden no está en estado pendiente de pago"
        )
    
    # Simulate payment processing with 80% success rate
    payment_success = random.random() < 0.8
    
    # Create payment record
    payment = Payment(
        order_id=payment_data.order_id,
        amount=order.total,
        payment_method=payment_data.payment_method,
        status=PaymentStatus.PAID if payment_success else PaymentStatus.FAILED,
        transaction_id=f"TX-{random.randint(10000, 99999)}",
        customer_id=payment_data.customer_id,
        payment_date=datetime.utcnow()
    )
    
    db.add(payment)
    db.flush()  # Get payment ID without committing
    
    if payment_success:
        # Create sale record
        sale = Sale(
            order_id=order.id,
            invoice_number=generate_invoice_number(db),
            total_amount=order.total,
            tax_amount=calculate_tax(order.total),
            payment_id=payment.id,
            status=PaymentStatus.PAID
        )
        
        db.add(sale)
        
        # Update order status
        order.status = "paid"
        order.payment_date = datetime.utcnow()
        
        # Schedule email notification
        background_tasks.add_task(
            send_payment_confirmation,
            order.user.email,
            order.id,
            sale.invoice_number
        )
        
        db.commit()
        
        return PaymentResponse(
            id=payment.id,
            order_id=order.id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status,
            transaction_id=payment.transaction_id,
            payment_date=payment.payment_date,
            invoice_number=sale.invoice_number
        )
    else:
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El pago no pudo ser procesado. Por favor intente nuevamente."
        )
