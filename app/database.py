from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
import os

load_dotenv()

# URL por defecto si no se encuentra en las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en las variables de entorno")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Importar todos los modelos aquí
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart
from app.models.orders import Order
from app.models.order_history import OrderHistory
from app.models.sales import Sale

# Crear todas las tablas
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()