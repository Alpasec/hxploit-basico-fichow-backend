from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.coupon import DiscountType

class CouponBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    discount_type: DiscountType
    discount_value: Decimal = Field(gt=0)
    max_uses: Optional[int] = Field(default=None, gt=0)
    min_purchase_amount: Decimal = Field(default=Decimal('0.00'), ge=0)
    is_active: bool = True
    expires_at: Optional[datetime] = None

class CouponCreate(CouponBase):
    pass

class CouponUpdate(BaseModel):
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[Decimal] = Field(default=None, gt=0)
    max_uses: Optional[int] = Field(default=None, gt=0)
    min_purchase_amount: Optional[Decimal] = Field(default=None, ge=0)
    expires_at: Optional[datetime] = None

class CouponStatusUpdate(BaseModel):
    is_active: bool

class CouponResponse(CouponBase):
    id: int
    used_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CouponValidateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    subtotal: Decimal = Field(ge=0)
