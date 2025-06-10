from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import product as models
from app.schemas import product as schemas
from app.utils import get_current_user, check_rol
from app.models.user import User

router = APIRouter(
    prefix="/products",
    tags=["products"]
)
# Agregar Nuevos productos, solo si es vendedor o admin
@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        print(f"Error creando el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# Listar todos los productos
@router.get("/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        products = db.query(models.Product).offset(skip).limit(limit).all()
        return products
    except Exception as e:
        print(f"Error leyendo los productos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

        
@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product
    except Exception as e:
        print(f"Error leyendo el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


#actualizar un producto segun su ID
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        print(f"Error actualizando el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
# Eliminar un producto segun su ID
@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["admin"]))
):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        db.delete(db_product)
        db.commit()
        return db_product
    except Exception as e:
        print(f"Error eliminando el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")