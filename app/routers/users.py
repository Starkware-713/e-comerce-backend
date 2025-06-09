from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import user as models
from app.schemas import user as schemas
from app.utils import get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            return JSONResponse(status_code=400, content={"detail": "Email already registered"})

        hashed_password = get_password_hash(user.password)
        db_user = models.User(email=user.email, hashed_password=hashed_password)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        print(f"Error reading users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        return db_user
    except Exception as e:
        print(f"Error reading user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")