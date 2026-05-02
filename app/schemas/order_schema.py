from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    coupon_code: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    coupon_id: Optional[int] = None
    subtotal: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
