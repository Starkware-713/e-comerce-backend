from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import PaymentRequest, PaymentResponse, PaymentStatus
from app.models.sales import Payment, Sale
from app.models.orders import Order
from app.models.user import User
from app.utils.mail_sender import send_payment_confirmation
from app.utils import get_current_user
from datetime import datetime
import mercadopago
import os
from dotenv import load_dotenv
import random
from typing import Optional

load_dotenv()

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

# Inicializar SDK de Mercado Pago
sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))

def generate_invoice_number(db: Session) -> int:
    """Generate a unique invoice number"""
    last_sale = db.query(Sale).order_by(Sale.invoice_number.desc()).first()
    if last_sale:
        return last_sale.invoice_number + 1
    return 1000  # Start from 1000

def calculate_tax(amount: float) -> float:
    """Calculate tax amount (IVA 21%)"""
    return amount * 0.21

@router.post("/create-preference")
async def create_payment_preference(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Obtener la orden
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this order")

        # Crear items para Mercado Pago
        items = []
        total_amount = 0

        for item in order.items:
            product = item.product
            item_data = {
                "title": product.name,
                "quantity": item.quantity,
                "currency_id": "ARS",  # Cambiar según tu país
                "unit_price": float(product.price),
                "description": product.description[:256],  # MP tiene un límite de caracteres
            }
            items.append(item_data)
            total_amount += float(product.price) * item.quantity

        # Crear preferencia de pago
        preference_data = {
            "items": items,
            "external_reference": str(order_id),
            "payer": {
                "name": current_user.name,
                "surname": current_user.lastname,
                "email": current_user.email,
            },
            "back_urls": {
                "success": os.getenv("MP_SUCCESS_URL"),
                "failure": os.getenv("MP_FAILURE_URL"),
                "pending": os.getenv("MP_PENDING_URL")
            },
            "notification_url": os.getenv("MP_NOTIFICATION_URL"),
            "auto_return": "approved",
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        # Crear registro de pago pendiente
        payment = Payment(
            order_id=order_id,
            amount=total_amount,
            status=PaymentStatus.PENDING,
            payment_method="mercado_pago",
            payment_date=datetime.utcnow()
        )
        db.add(payment)
        db.commit()

        return {
            "init_point": preference["init_point"],
            "preference_id": preference["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/success")
async def payment_success(
    payment_id: str, 
    status: str, 
    external_reference: str,
    db: Session = Depends(get_db)
):
    try:
        order_id = int(external_reference)
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update payment status
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if payment:
            payment.status = PaymentStatus.COMPLETED
            payment.mp_payment_id = payment_id
            payment.payment_date = datetime.utcnow()
            
            # Create sale record
            sale = Sale(
                order_id=order_id,
                payment_id=payment.id,
                sale_date=datetime.utcnow(),
                total_amount=payment.amount,
                tax_amount=calculate_tax(payment.amount),
                invoice_number=generate_invoice_number(db)
            )
            db.add(sale)
            
            # Update order status
            order.status = "completed"
            
            db.commit()

            # Send confirmation email
            background_tasks = BackgroundTasks()
            background_tasks.add_task(
                send_payment_confirmation,
                order.user.email,
                order.id,
                payment.amount
            )

            return {"message": "Payment processed successfully", "order_id": order_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/failure")
async def payment_failure(
    payment_id: Optional[str] = None, 
    status: str = "failed", 
    external_reference: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if external_reference:
        try:
            order_id = int(external_reference)
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()
            if payment:
                payment.status = PaymentStatus.FAILED
                payment.mp_payment_id = payment_id
                payment.payment_date = datetime.utcnow()
                db.commit()
        except:
            pass
    
    return {"message": "Payment failed", "status": status}

@router.get("/pending")
async def payment_pending(
    payment_id: str, 
    status: str, 
    external_reference: str,
    db: Session = Depends(get_db)
):
    try:
        order_id = int(external_reference)
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        if payment:
            payment.status = PaymentStatus.PENDING
            payment.mp_payment_id = payment_id
            payment.payment_date = datetime.utcnow()
            db.commit()
            
        return {"message": "Payment is pending", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        
        if data["type"] == "payment":
            payment_info = sdk.payment().get(data["data"]["id"])
            
            if payment_info["status"] == 200:
                payment_data = payment_info["response"]
                order_id = int(payment_data["external_reference"])
                
                payment = db.query(Payment).filter(Payment.order_id == order_id).first()
                if payment:
                    # Update payment status based on MP status
                    mp_status = payment_data["status"]
                    if mp_status == "approved":
                        payment.status = PaymentStatus.COMPLETED
                    elif mp_status == "rejected":
                        payment.status = PaymentStatus.FAILED
                    else:
                        payment.status = PaymentStatus.PENDING
                    
                    payment.mp_payment_id = str(payment_data["id"])
                    payment.payment_date = datetime.utcnow()
                    
                    # If payment is completed, create sale record
                    if mp_status == "approved":
                        sale = Sale(
                            order_id=order_id,
                            payment_id=payment.id,
                            sale_date=datetime.utcnow(),
                            total_amount=payment.amount,
                            tax_amount=calculate_tax(payment.amount),
                            invoice_number=generate_invoice_number(db)
                        )
                        db.add(sale)
                        
                        # Update order status
                        order = db.query(Order).filter(Order.id == order_id).first()
                        if order:
                            order.status = "completed"
                    
                    db.commit()
                    
                    # Send confirmation email for completed payments
                    if mp_status == "approved":
                        background_tasks = BackgroundTasks()
                        background_tasks.add_task(
                            send_payment_confirmation,
                            order.user.email,
                            order_id,
                            payment.amount
                        )
        
        return {"message": "Webhook processed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
