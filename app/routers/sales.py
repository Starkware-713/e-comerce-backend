from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import product as models
from app.schemas import product as schemas
from app.utils import get_current_user, check_rol
from app.models.user import User

router = APIRouter(
    prefix="/sales",
    tags=["sales"]
)

# Facturas pendientes por fecha
@router.get("/pending", response_model=list[schemas.Sale])
def read_pending_sales(db: Session = Depends(get_db)):
    try:
        sales = db.query(models.Sale).filter(models.Sale.is_active == True).all()
        return sales
    except Exception as e:
        print(f"Error leyendo las ventas pendientes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

#venta pendiente por ID del cliente
@router.get("/pending/{client_id}", response_model=schemas.Sale)
def read_pending_sales_by_client(client_id: int, db: Session = Depends(get_db)):
    try:
        sale = db.query(models.Sale).filter(models.Sale.is_active == True, models.Sale.client_id == client_id).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return sale
    except Exception as e:
        print(f"Error leyendo la venta pendiente: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
#resumen de las ventas activas
@router.get('/summary', response_model=list[schemas.Sale])
def get_sales_summary(db: Session = Depends(get_db)):
    try:
        sales = db.query(models.Sale).filter(models.Sale.is_active == True).all()
        if not sales:
            raise HTTPException(status_code=404, detail="No hay ventas activas")
        return sales
    except Exception as e:
        print(f"Error obteniendo el resumen de ventas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")