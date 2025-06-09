from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="La contraseña debe tener entre 8 y 128 caracteres")

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True