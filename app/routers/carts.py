from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import cart as models
from app.schemas import cart as schemas
from app.utils import get_current_user
from app.models.user import User
from app.models.coupon import Coupon
from datetime import datetime
from app.utils.ai import generate_ai_completion
from fastapi import Body

router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)
# Crear un carrito de compras 
@router.post("/", response_model=schemas.Cart)
def create_cart(
    cart: schemas.CartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Buscar si el usuario ya tiene un carrito activo
        db_cart = db.query(models.Cart).filter(models.Cart.user_id == cart.user_id, models.Cart.status == "active").first()
        if db_cart:
            # Si ya existe, limpiar los items actuales del carrito
            db.query(models.CartItem).filter(models.CartItem.cart_id == db_cart.id).delete()
        else:
            db_cart = models.Cart(user_id=cart.user_id)
            db.add(db_cart)
            db.flush()  # Para obtener el id del carrito
        for item in cart.items:
            # Validar que el producto existe
            product = db.query(models.Product).filter(models.Product.id == item.product.id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto con id {item.product.id} no encontrado")
            cart_item = models.CartItem(
                cart_id=db_cart.id,
                product_id=product.id,
                quantity=item.quantity
            )
            db.add(cart_item)
        db.commit()
        # Recargar el carrito con los items y productos asociados
        db.refresh(db_cart)
        cart_with_items = db.query(models.Cart).options(
            joinedload(models.Cart.user),
            joinedload(models.Cart.items).joinedload(models.CartItem.product)
        ).filter(models.Cart.id == db_cart.id).first()
        return cart_with_items
    except Exception as e:
        db.rollback()
        print(f"Error creando el carrito: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
@router.get("/", response_model=list[schemas.Cart])
def read_carts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        carts = (
            db.query(models.Cart)
            .filter(models.Cart.user_id == current_user.id)  
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
    
#listar el carrito de un usuario segun el ID
@router.get("/{cart_id}", response_model=schemas.Cart)
def read_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

#Agregar un producto al carrito segun el ID del carrito y el ID del producto
@router.put("/{cart_id}/add", response_model=schemas.Cart)
def add_product_to_cart(
    cart_id: int,
    product: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == current_user.id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado o no pertenece al usuario")

        existing_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart_id,
            models.CartItem.product_id == product.product.id
        ).first()

        if existing_item:
            existing_item.quantity += product.quantity
        else:
            new_item = models.CartItem(
                cart_id=cart_id,
                product_id=product.product.id,
                quantity=product.quantity
            )
            db.add(new_item)

        db.commit()
        db.refresh(cart)
        return cart
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

#actualizar la cantidad de un producto en el carrito
@router.put("/{cart_id}/product/{product_id}", response_model=schemas.Cart)
def update_product_quantity_in_cart(
    cart_id: int,
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == current_user.id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado o no pertenece al usuario")
        
        cart_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart_id,
            models.CartItem.product_id == product_id
        ).first()

        if not cart_item:
            raise HTTPException(status_code=404, detail="El producto no está en el carrito")

        if quantity <= 0:
            db.delete(cart_item)
        else:
            cart_item.quantity = quantity

        db.commit()
        return cart
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

#eliminacion de un producto en un carrito basado en el ID del carrito y el ID del producto
@router.delete("/{cart_id}/product/{product_id}", status_code=204)
def delete_product_from_cart(
    cart_id: int,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Corrige la referencia a User
):
    try:
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == current_user.id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado o no pertenece al usuario")
        cart_item = db.query(models.CartItem).filter(
            models.CartItem.cart_id == cart_id,
            models.CartItem.product_id == product_id
        ).first()

        if not cart_item:
            raise HTTPException(status_code=404, detail="El producto no está en el carrito")

        db.delete(cart_item)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/{cart_id}/apply-coupon", response_model=schemas.Cart)
async def apply_coupon(
    cart_id: int,
    coupon_request: schemas.ApplyCouponRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Verificar si el carrito existe y pertenece al usuario
        cart = db.query(models.Cart).filter(
            models.Cart.id == cart_id,
            models.Cart.user_id == current_user.id,
            models.Cart.status == "active"
        ).first()
        
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado o no está activo")

        # Validar el cupón
        coupon = db.query(Coupon).filter(Coupon.code == coupon_request.code).first()
        if not coupon:
            raise HTTPException(status_code=404, detail="Cupón no encontrado")

        if not coupon.is_active:
            raise HTTPException(status_code=400, detail="Cupón no está activo")

        if coupon.current_uses >= coupon.max_uses:
            raise HTTPException(status_code=400, detail="Cupón ha alcanzado el máximo de usos")

        now = datetime.utcnow()
        if now < coupon.valid_from or now > coupon.valid_until:
            raise HTTPException(status_code=400, detail="Cupón no es válido en este momento")

        # Calcular el descuento
        total = sum(item.quantity * item.product.price for item in cart.items)
        discount = total * (coupon.discount_percent / 100)

        # Actualizar el carrito con el cupón
        cart.coupon_id = coupon.id
        cart.discount_amount = discount

        db.commit()
        db.refresh(cart)
        return cart

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Modificar la función de checkout para incluir el manejo de cupones
@router.put("/{cart_id}/checkout", response_model=schemas.Cart)
def checkout_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cart = db.query(models.Cart).filter(
            models.Cart.id == cart_id,
            models.Cart.user_id == current_user.id,
            models.Cart.status == "active"
        ).first()
        
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado o no está activo")

        # Si hay un cupón aplicado, incrementar su contador de usos
        if cart.coupon_id:
            coupon = db.query(Coupon).filter(Coupon.id == cart.coupon_id).first()
            if coupon:
                coupon.current_uses += 1
                if coupon.current_uses >= coupon.max_uses:
                    coupon.is_active = False

        cart.status = "completed"
        db.commit()
        db.refresh(cart)
        return cart
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

#Eliminacion del carrito segun el id y el usuario autenticado
@router.delete("/{cart_id}", response_model=schemas.Cart)
def delete_cart(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cart = db.query(models.Cart).filter(models.Cart.id == cart_id, models.Cart.user_id == current_user.id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Carrito no encontrado")
        # Eliminar primero los items asociados al carrito
        db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
        db.delete(cart)
        db.commit()
        return cart
    except Exception as e:
        db.rollback()
        print(f"Error eliminando el carrito {cart_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
