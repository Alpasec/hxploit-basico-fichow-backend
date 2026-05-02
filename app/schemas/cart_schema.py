from pydantic import BaseModel, Field
from typing import Any, List, Optional
from datetime import datetime
from decimal import Decimal
from app.schemas.product_schema import ProductResponse

class CartItemCreate(BaseModel):
    product_id: int
    quantity: Any

class CartItemUpdate(BaseModel):
    quantity: Any

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
    product: Optional[ProductResponse] = None
    subtotal: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = Field(default_factory=list)
    total: Decimal = Decimal('0.00')
    
    class Config:
        from_attributes = True

class CartValidateRequest(BaseModel):
    coupon_code: Optional[str] = None
