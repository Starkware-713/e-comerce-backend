from fastapi import APIRouter, Depends, HTTPException
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
    request: EmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        prompt = request.template.prompt
        system_message = "Eres un experto en diseño de emails. Genera un HTML de email profesional y responsivo según el siguiente prompt. devuelve solamente el HTML sin etiquetas adicionales ni explicaciones."
        html_content = generate_ai_completion(prompt, system_message)
        if not html_content:
            raise Exception("No se pudo generar el HTML del email.")
        return EmailResponse(message="HTML generado exitosamente", preview_html=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/send-email")
def send_email(request: EmailRequest):
    """
    Envía un email real usando el HTML generado y los datos del request.
    """
    try:
        # Determinar el tipo de email y enviar usando la función adecuada
        if request.template.type == EmailType.MARKETING:
            # Usar el HTML generado en el prompt como cuerpo
            html_content = request.template.prompt
            enviado = send_marketing_email(
                to_email=request.to_email,
                subject=request.subject,
                content=html_content,
                marketing_message=html_content
            )
        elif request.template.type == EmailType.WELCOME:
            username = request.user_context.name if request.user_context else "Usuario"
            enviado = send_welcome_email(
                to_email=request.to_email,
                username=username
            )
        elif request.template.type == EmailType.ORDER_CONFIRMATION:
            # Se requieren variables: order_number, total_amount, items
            vars = request.content_variables or {}
            enviado = send_order_confirmation(
                to_email=request.to_email,
                order_number=vars.get("order_number", ""),
                total_amount=vars.get("total_amount", 0),
                items=vars.get("items", [])
            )
        elif request.template.type == EmailType.PROMOTION:
            html_content = request.template.prompt
            enviado = send_marketing_email(
                to_email=request.to_email,
                subject=request.subject,
                content=html_content,
                marketing_message=html_content
            )
        else:
            # Por defecto, enviar como marketing
            html_content = request.template.prompt
            enviado = send_marketing_email(
                to_email=request.to_email,
                subject=request.subject,
                content=html_content,
                marketing_message=html_content
            )
        if not enviado:
            raise Exception("No se pudo enviar el email.")
        return JSONResponse(content={"message": "Email enviado exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
