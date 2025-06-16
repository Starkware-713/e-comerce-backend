from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    lastname: str = Field(..., min_length=2, max_length=100, description="Apellido del usuario")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="La contraseña debe tener entre 8 y 128 caracteres")

class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100, description="Nombre del usuario")
    lastname: str | None = Field(None, min_length=2, max_length=100, description="Apellido del usuario")
    email: EmailStr | None = None

class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=8, description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")
    confirm_password: str = Field(..., min_length=8, description="Confirmar nueva contraseña")

class User(UserBase):
    id: int
    is_active: bool
    rol: str

    class Config:
        from_attributes = True