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

@router.post("/webhook")
async def payment_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        
        if data["type"] == "payment":
            payment_info = sdk.payment().get(data["data"]["id"])
            payment_data = payment_info["response"]
            
            order_id = int(payment_data["external_reference"])
            status = payment_data["status"]
            
            # Actualizar el pago en la base de datos
            payment = db.query(Payment).filter(Payment.order_id == order_id).first()
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            # Mapear estados de Mercado Pago a nuestros estados
            status_map = {
                "approved": PaymentStatus.PAID,
                "rejected": PaymentStatus.FAILED,
                "pending": PaymentStatus.PENDING
            }
            
            payment.status = status_map.get(status, PaymentStatus.PENDING)
            payment.transaction_id = str(payment_data["id"])
            
            if status == "approved":
                # Generar número de factura solo si el pago fue aprobado
                payment.invoice_number = generate_invoice_number(db)
                
                # Crear venta
                sale = Sale(
                    order_id=order_id,
                    payment_id=payment.id,
                    invoice_number=payment.invoice_number,
                    total_amount=payment_data["transaction_amount"],
                    tax_amount=calculate_tax(payment_data["transaction_amount"]),
                    sale_date=datetime.utcnow()
                )
                db.add(sale)
                
                # Enviar email de confirmación
                order = db.query(Order).filter(Order.id == order_id).first()
                if order and order.user:
                    background_tasks.add_task(
                        send_payment_confirmation,
                        email=order.user.email,
                        order_id=order_id,
                        amount=payment_data["transaction_amount"],
                        invoice_number=payment.invoice_number
                    )

            db.commit()
            return {"status": "success"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/success")
async def payment_success(
    payment_id: str,
    status: str,
    external_reference: str,
):
    return {
        "message": "Payment successful",
        "payment_id": payment_id,
        "status": status,
        "order_id": external_reference
    }

@router.get("/failure")
async def payment_failure(
    payment_id: Optional[str] = None,
    status: Optional[str] = None,
    external_reference: Optional[str] = None,
):
    return {
        "message": "Payment failed",
        "payment_id": payment_id,
        "status": status,
        "order_id": external_reference
    }

@router.get("/pending")
async def payment_pending(
    payment_id: str,
    status: str,
    external_reference: str,
):
    return {
        "message": "Payment pending",
        "payment_id": payment_id,
        "status": status,
        "order_id": external_reference
    }
