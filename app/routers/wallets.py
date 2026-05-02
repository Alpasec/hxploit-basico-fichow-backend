from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wallet_schema import WalletResponse, TopUpRequest, AdjustRequest
from app.services import wallet_service
from app.utils.response import success_response
from app.dependencies.auth_dependency import get_current_user
from app.dependencies.role_dependency import get_admin_user
from app.models.user import User
from app.exceptions import forbidden

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("/me", response_model=None)
def get_my_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = wallet_service.get_wallet_by_user_id(db, current_user.id)
    return success_response(data=WalletResponse.model_validate(wallet).model_dump())

@router.get("/{wallet_id}", response_model=None)
def get_wallet(wallet_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = wallet_service.get_wallet_by_id(db, wallet_id)
    if current_user.role.value != "ADMIN" and wallet.user_id != current_user.id:
        raise forbidden()
    return success_response(data=WalletResponse.model_validate(wallet).model_dump())

@router.get("", response_model=None)
def get_wallets(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    wallets = wallet_service.get_wallets(db)
    return success_response(data=[WalletResponse.model_validate(w).model_dump() for w in wallets])

@router.post("/top-up", response_model=None)
def top_up_wallet(request: TopUpRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wallet = wallet_service.top_up_wallet(db, current_user.id, request)
    return success_response(data=WalletResponse.model_validate(wallet).model_dump(), message="Wallet topped up successfully")

@router.post("/{wallet_id}/adjust", response_model=None)
def adjust_wallet(wallet_id: int, request: AdjustRequest, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    wallet = wallet_service.adjust_wallet(db, wallet_id, request)
    return success_response(data=WalletResponse.model_validate(wallet).model_dump(), message="Wallet adjusted successfully")
