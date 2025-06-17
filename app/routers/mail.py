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
from app.services.email_service import generate_email_content, get_template_prompt
from app.utils.mail_sender import send_order_confirmation
from typing import Optional

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

@router.post("/send", response_model=EmailResponse)
async def send_email(request: EmailRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Send an email with AI-generated content based on template and context
    """
    try:
        # Generate HTML content
        html_content = generate_email_content(
            template=request.template,
            user_context=request.user_context,
            content_variables=request.content_variables
        )
        
        if not html_content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate email content"
            )
        
        # Send email using existing mail_sender functionality
        success = send_order_confirmation(
            to_email=request.to_email,
            subject=request.subject,
            content=html_content
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
        
        return EmailResponse(
            message="Email sent successfully",
            preview_html=html_content
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/preview", response_class=HTMLResponse)
async def preview_email(
    request: PreviewEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate and preview email content without sending it
    """
    try:
        html_content = generate_email_content(
            template=request.template,
            user_context=request.user_context,
            content_variables=request.content_variables
        )
        
        if not html_content:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate email preview"
            )
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/templates/{email_type}")
async def get_default_template(
    email_type: EmailType,
    current_user: User = Depends(get_current_user)
):
    """
    Get default template prompt for a specific email type
    """
    prompt = get_template_prompt(email_type)
    
    if not prompt:
        raise HTTPException(
            status_code=404,
            detail=f"No default template found for type: {email_type}"
        )
    
    return {
        "type": email_type,
        "prompt": prompt
    }