from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.transaction_schema import TransactionResponse
from app.services import transaction_service
from app.utils.response import success_response
from app.dependencies.role_dependency import get_admin_user
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.exceptions import forbidden

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/me", response_model=None)
def get_my_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = transaction_service.get_transactions(db, user_id=current_user.id)
    return success_response(data=[TransactionResponse.model_validate(t).model_dump() for t in transactions])

@router.get("/{transaction_id}", response_model=None)
def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transaction = transaction_service.get_transaction_by_id(db, transaction_id)
    return success_response(data=TransactionResponse.model_validate(transaction).model_dump())

@router.get("", response_model=None)
def get_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = transaction_service.get_transactions(db)
    return success_response(data=[TransactionResponse.model_validate(t).model_dump() for t in transactions])
