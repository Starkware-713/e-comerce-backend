from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.permissions import get_current_user
from app.schemas.email import (
    EmailRequest,
    PreviewEmailRequest,
    EmailResponse,
    EmailType
)
from app.utils.ai import generate_ai_completion
from app.utils.mail_sender import send_marketing_email, send_welcome_email, send_order_confirmation, send_payment_confirmation
from typing import Optional

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

@router.post("/prompt-IA")
def send_prompt_to_groq(
    prompt: str = Body(..., embed=True, description="Prompt para la IA")
):
    try:
        system_message = (
            'Eres un experto en diseño de emails. Tu tarea es generar únicamente el fragmento central de HTML para un email profesional, visualmente atractivo y completamente responsivo.'
            'No incluyas etiquetas como <!DOCTYPE html>, <html>, <head>, <body>, <table> generales ni ningún envoltorio global.'
            'No utilices tablas para la estructura exterior del email.'
            'Usa solo HTML y CSS embebido en línea para el contenido central del email.'
            'Aplica una estética moderna, profesional y agradable, usando una paleta de colores basada en azules y verdes.'
            'No generes markdown, explicaciones ni comentarios. Devuelve exclusivamente el fragmento HTML necesario para ser insertado dentro de un sistema de mailing.'
            'Asegúrate de que el diseño sea compatible con clientes de correo populares y que pueda adaptarse correctamente en dispositivos móviles.'
        )
        html_content = generate_ai_completion(prompt, system_message)
        if not html_content:
            raise Exception("No se pudo generar el HTML del email.")
        return EmailResponse(message="HTML generado exitosamente", preview_html=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/send-email")
def send_email(request: EmailRequest):
    try:
        if request.template.type == EmailType.MARKETING:
            html_content = request.template.prompt
            if not html_content:
                raise HTTPException(status_code=400, detail="El campo 'prompt' (HTML) es requerido para emails de marketing.")
            enviado = send_marketing_email(
                to_email=request.to_email,
                subject=request.subject,
                content=html_content,
                marketing_message=html_content
            )
        elif request.template.type == EmailType.WELCOME:
            if not request.user_context or not request.user_context.name:
                raise HTTPException(status_code=400, detail="El nombre de usuario es requerido para emails de bienvenida.")
            username = request.user_context.name
            enviado = send_welcome_email(
                to_email=request.to_email,
                username=username
            )
        elif request.template.type == EmailType.ORDER_CONFIRMATION:
            vars = request.content_variables or {}
            if not vars.get("order_number") or not vars.get("total_amount") or not vars.get("items"):
                raise HTTPException(status_code=400, detail="'order_number', 'total_amount' e 'items' son requeridos para confirmación de orden.")
            enviado = send_order_confirmation(
                to_email=request.to_email,
                order_number=vars.get("order_number"),
                total_amount=vars.get("total_amount"),
                items=vars.get("items")
            )
        elif request.template.type == EmailType.PROMOTION:
            html_content = request.template.prompt
            if not html_content:
                raise HTTPException(status_code=400, detail="El campo 'prompt' (HTML) es requerido para emails de promoción.")
            enviado = send_marketing_email(
                to_email=request.to_email,
                subject=request.subject,
                content=html_content,
                marketing_message=html_content
            )
        else:
            html_content = request.template.prompt
            if not html_content:
                raise HTTPException(status_code=400, detail="El campo 'prompt' (HTML) es requerido para este tipo de email.")
            enviado = send_marketing_email(
                to_email=request.to_email,
                subject=request.subject,
                content=html_content,
                marketing_message=html_content
            )
        if not enviado:
            raise HTTPException(status_code=500, detail="No se pudo enviar el email.")
        return JSONResponse(content={"message": "Email enviado exitosamente"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
