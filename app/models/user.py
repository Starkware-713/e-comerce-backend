from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.models import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    VENDEDOR = "vendedor"
    COMPRADOR = "comprador"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    rol = Column(String, default=UserRole.COMPRADOR)