from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import cart as models
from app.schemas import cart as schemas

router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)
@router.post("/", response_model=schemas.Cart)
def create_cart(cart: schemas.CartCreate, db: Session = Depends(get_db)):
    try:
        # Crear el carrito
        db_cart = models.Cart(user_id=cart.user_id)
        db.add(db_cart)
        db.flush()  # Para obtener el ID del carrito
        
        # Crear los items del carrito
        for item in cart.items:
            cart_item = models.CartItem(
                cart_id=db_cart.id,
                product_id=item.product.id,
                quantity=item.quantity
            )
            db.add(cart_item)
        
        db.commit()
        db.refresh(db_cart)
        return db_cart
    except Exception as e:
        print(f"Error creando el carrito: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
@router.get("/", response_model=list[schemas.Cart])
def read_carts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        carts = (
            db.query(models.Cart)
            .options(
                joinedload(models.Cart.user),
                joinedload(models.Cart.items).joinedload(models.CartItem.product)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        return carts
    except Exception as e:
        print(f"Error leyendo los carritos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{cart_id}", response_model=schemas.Cart)
def read_cart(cart_id: int, db: Session = Depends(get_db)):
    try:
        cart = (
            db.query(models.Cart)
            .options(
                joinedload(models.Cart.user),
                joinedload(models.Cart.items).joinedload(models.CartItem.product)
            )
            .filter(models.Cart.id == cart_id)
            .first()
        )
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado")
        return cart
    except Exception as e:
        print(f"Error leyendo el carrito {cart_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")