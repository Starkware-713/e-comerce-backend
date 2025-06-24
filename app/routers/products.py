from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.database import get_db
from app.models import product as models
from app.schemas import product as schemas
from app.utils import get_current_user, check_rol
from app.models.user import User

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# Agregar Nuevos productos, solo si es vendedor
@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor"]))
):
    try:
        db_product = models.Product(**product.dict())
        db_product.created_by = current_user.id
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        print(f"Error creando el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/search", response_model=List[schemas.Product])
def search_products(
    toFind: str,
    db: Session = Depends(get_db)
):
    try:
        products = db.query(models.Product).filter(
            models.Product.name.ilike(f"%{toFind}%") |
            models.Product.description.ilike(f"%{toFind}%")
        ).all()
        return products
    except Exception as e:
        print(f"Error buscando productos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Listar todos los productos
@router.get("/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = Query("none", enum=["none", "price_asc", "price_desc", "newest"]),
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(models.Product)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                models.Product.name.ilike(f"%{search}%") |
                models.Product.description.ilike(f"%{search}%")
            )
        
        if category:
            query = query.filter(models.Product.category == category)
            
        if min_price is not None:
            query = query.filter(models.Product.price >= min_price)
            
        if max_price is not None:
            query = query.filter(models.Product.price <= max_price)
            
        if in_stock is not None:
            query = query.filter(models.Product.stock > 0 if in_stock else models.Product.stock == 0)
        
        # Aplicar ordenamiento
        if sort == "price_asc":
            query = query.order_by(models.Product.price)
        elif sort == "price_desc":
            query = query.order_by(desc(models.Product.price))
        elif sort == "newest":
            query = query.order_by(desc(models.Product.created_at))
        # Si sort es 'none', no se aplica ningún ordenamiento
        products = query.offset(skip).limit(limit).all()
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
        raise HTTPException(status_code=404, detail="Producto no encontrado")


#actualizar un producto segun su ID
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        # Actualizar solo los campos proporcionados
        for field, value in product_update.dict(exclude_unset=True).items():
            setattr(db_product, field, value)
            
        db_product.updated_at = datetime.utcnow()
        db_product.updated_by = current_user.id
        
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        print(f"Error actualizando el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# Eliminar un producto segun su ID
@router.delete("/{product_id}")
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
        return {"message": "Producto eliminado exitosamente"}
    except Exception as e:
        print(f"Error eliminando el producto: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.patch("/{product_id}/stock", response_model=schemas.Product)
def update_stock(
    product_id: int,
    stock_update: schemas.StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["vendedor", "admin"]))
):
    try:
        db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        db_product.stock = stock_update.stock
        db_product.updated_at = datetime.utcnow()
        db_product.updated_by = current_user.id
        
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        print(f"Error actualizando el stock: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")