from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    currency: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TopUpRequest(BaseModel):
    amount: Decimal = Field(gt=0)

class AdjustRequest(BaseModel):
    amount: Decimal = Field(ge=0)
    type: str = Field(pattern="^(ADD|SUBTRACT|SET)$")
