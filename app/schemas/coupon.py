from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CouponBase(BaseModel):
    code: str = Field(..., description="Unique coupon code")
    discount_percent: float = Field(..., ge=0, le=100, description="Discount percentage between 0 and 100")
    valid_from: Optional[datetime] = Field(default_factory=datetime.utcnow)
    valid_until: datetime
    max_uses: int = Field(..., gt=0, description="Maximum number of times this coupon can be used")
    is_active: bool = True

class CouponCreate(CouponBase):
    pass

class CouponUpdate(BaseModel):
    code: Optional[str] = None
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

class CouponResponse(CouponBase):
    id: int
    current_uses: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True