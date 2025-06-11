from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.sales import Sale as SaleModel
from app.schemas import sales as schemas
from app.utils.permissions import check_rol
from app.models.user import User

router = APIRouter(
    prefix="/sales",
    tags=["sales"]
)

# Facturas pendientes
@router.get("/pending", response_model=list[schemas.Sale])
def read_pending_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        sales = (
            db.query(SaleModel)
            .filter(SaleModel.status == "pending")
            .options(
                joinedload(SaleModel.items).joinedload(SaleModel.product),
                joinedload(SaleModel.user)
            )
            .order_by(SaleModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return sales
    except Exception as e:
        print(f"Error leyendo las ventas pendientes: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Obtener una venta específica
@router.get("/{sale_id}", response_model=schemas.Sale)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        sale = (
            db.query(SaleModel)
            .filter(SaleModel.id == sale_id)
            .options(
                joinedload(SaleModel.items).joinedload(SaleModel.product),
                joinedload(SaleModel.user)
            )
            .first()
        )
        if not sale:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return sale
    except Exception as e:
        print(f"Error leyendo la venta: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
# Resumen de ventas por estado
@router.get("/summary/{status}", response_model=list[schemas.Sale])
def get_sales_summary(
    status: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        if status not in ["pending", "completed", "cancelled"]:
            raise HTTPException(
                status_code=400,
                detail="Estado no válido. Estados permitidos: pending, completed, cancelled"
            )

        sales = (
            db.query(SaleModel)
            .filter(SaleModel.status == status)
            .options(
                joinedload(SaleModel.items).joinedload(SaleModel.product),
                joinedload(SaleModel.user)
            )
            .order_by(SaleModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return sales
    except Exception as e:
        print(f"Error obteniendo el resumen de ventas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")