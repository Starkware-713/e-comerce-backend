from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.schemas.user import UserBase

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    rol: Optional[str] = None
    exp: Optional[datetime] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterRequest(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial"
    )
    confirm_password: str = Field(..., min_length=8)
    rol: str = Field(default="comprador", description="Rol del usuario (comprador o vendedor)")
