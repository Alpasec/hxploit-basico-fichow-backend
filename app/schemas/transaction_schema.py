from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionType

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    wallet_id: int
    order_id: Optional[int] = None
    type: TransactionType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
