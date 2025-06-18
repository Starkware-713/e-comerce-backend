from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponResponse, CouponUpdate
from app.utils.permissions import get_current_user

router = APIRouter(
    prefix="/coupons",
    tags=["coupons"]
)

@router.post("/", response_model=CouponResponse)
async def create_coupon(
    coupon: CouponCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_sales_manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales managers can create coupons"
        )
    
    db_coupon = Coupon(
        code=coupon.code,
        discount_percent=coupon.discount_percent,
        valid_from=coupon.valid_from,
        valid_until=coupon.valid_until,
        max_uses=coupon.max_uses,
        is_active=coupon.is_active
    )
    
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

@router.get("/", response_model=List[CouponResponse])
async def get_coupons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_sales_manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales managers can view all coupons"
        )
    
    return db.query(Coupon).all()

@router.get("/validate/{code}", response_model=CouponResponse)
async def validate_coupon(
    code: str,
    db: Session = Depends(get_db)
):
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    if not coupon.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is not active"
        )
    
    if coupon.current_uses >= coupon.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon has reached maximum uses"
        )
    
    now = datetime.utcnow()
    if now < coupon.valid_from or now > coupon.valid_until:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon is not valid at this time"
        )
    
    return coupon

@router.patch("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: int,
    coupon_update: CouponUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not current_user.get("is_sales_manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sales managers can update coupons"
        )
    
    db_coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not db_coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    for field, value in coupon_update.dict(exclude_unset=True).items():
        setattr(db_coupon, field, value)
    
    db.commit()
    db.refresh(db_coupon)
    return db_coupon