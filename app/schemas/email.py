from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from enum import Enum

class EmailType(str, Enum):
    MARKETING = "marketing"
    WELCOME = "welcome"
    ORDER_CONFIRMATION = "order_confirmation"
    PROMOTION = "promotion"
    CUSTOM = "custom"

class EmailTemplate(BaseModel):
    type: EmailType
    prompt: str
    style: Optional[Dict[str, Any]] = None

class UserEmailContext(BaseModel):
    name: str
    email: EmailStr
    total_orders: Optional[int] = 0
    preferences: Optional[List[str]] = None
    last_purchase_date: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    template: EmailTemplate
    user_context: Optional[UserEmailContext] = None
    content_variables: Optional[Dict[str, Any]] = None

class PreviewEmailRequest(BaseModel):
    template: EmailTemplate
    user_context: Optional[UserEmailContext] = None
    content_variables: Optional[Dict[str, Any]] = None

class EmailResponse(BaseModel):
    message: str
    preview_html: Optional[str] = None
