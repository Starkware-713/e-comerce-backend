from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import auth as schemas
from app.utils import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    validate_password,
    verify_token,
    REFRESH_SECRET_KEY
)
from app.models import user as models
from app.utils import get_password_hash
from app.utils.mail_sender import send_welcome_email

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=schemas.Token)
async def register(user_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Validar que las contraseñas coincidan
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Las contraseñas no coinciden"
        )
    
    # Validar la seguridad de la contraseña
    validate_password(user_data.password)
    
    # Validar el rol
    if user_data.rol not in ["comprador", "vendedor"]:
        raise HTTPException(
            status_code=400,
            detail="Rol inválido. Debe ser 'comprador' o 'vendedor'"
        )
    
    # Crear el usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = models.User(
        email=user_data.email,
        name=user_data.name,
        lastname=user_data.lastname,
        hashed_password=hashed_password,
        rol=user_data.rol
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Enviar email de bienvenida
        send_welcome_email(
            to_email=db_user.email,
            username=user_data.name
        )
        
        # Generar tokens
        access_token = create_access_token(
            data={"sub": db_user.email, "rol": db_user.rol}
        )
        refresh_token = create_refresh_token(
            data={"sub": db_user.email, "rol": db_user.rol}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "rol": db_user.rol
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el usuario: {str(e)}"
        )

@router.post("/login", response_model=schemas.Token)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "rol": user.rol})
    refresh_token = create_refresh_token(data={"sub": user.email, "rol": user.rol})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "rol": user.rol
    }
    
    access_token = create_access_token(
        data={"sub": user.email, "rol": user.rol}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "rol": user.rol}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "rol": user.rol
    }

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        # Verificar el refresh token
        payload = verify_token(refresh_token, REFRESH_SECRET_KEY)
        email = payload.get("sub")
        rol = payload.get("rol")
        
        # Verificar que el usuario existe
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        # Generar nuevos tokens
        new_access_token = create_access_token(
            data={"sub": email, "rol": rol}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": email, "rol": rol}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo refrescar el token"
        )
