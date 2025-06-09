from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Password must be between 8 and 128 characters")

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True