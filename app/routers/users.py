from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import user as models
from app.schemas import user as schemas
from app.utils import get_password_hash, verify_password
from app.utils import get_current_user, check_rol
from app.models.user import User

router = APIRouter(
    prefix="/user",
    tags=["users"]
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            return JSONResponse(status_code=400, content={"detail": "Email already registered"})

        hashed_password = get_password_hash(user.password)
        db_user = models.User(
            email=user.email,
            name=user.name,
            lastname=user.lastname,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    except Exception as e:
        print(f"Error creando el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=list[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_rol(["admin"]))
):
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        print(f"Error leyendo usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/my-profile", response_model=schemas.User)
def get_user_profile(current_user: User = Depends(get_current_user)):
    try:
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "Usuario no encontrado"})
        return db_user
    except Exception as e:
        print(f"Error leyendo el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.put("/update-profile", response_model=schemas.User)
async def update_profile(
    user_data: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Verificar si el email ya existe
        if user_data.email and user_data.email != current_user.email:
            existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email ya registrado")
        
        # Actualizar solo los campos proporcionados
        if user_data.name is not None:
            current_user.name = user_data.name
        if user_data.lastname is not None:
            current_user.lastname = user_data.lastname
        if user_data.email is not None:
            current_user.email = user_data.email

        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        print(f"Error actualizando el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/change-password")
async def change_password(
    password_data: schemas.ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Verificar contraseña actual
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
        
        # Verificar que la nueva contraseña coincida con la confirmación
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
        
        # Verificar que la nueva contraseña sea diferente a la actual
        if password_data.current_password == password_data.new_password:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe ser diferente a la actual")
        
        # Actualizar la contraseña
        current_user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        print(f"Error cambiando la contraseña: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")