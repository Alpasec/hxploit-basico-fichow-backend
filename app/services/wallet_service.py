from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.models.transaction import Transaction, TransactionType
from app.schemas.wallet_schema import TopUpRequest, AdjustRequest
from app.exceptions import CustomException, user_not_found
from fastapi import status

def get_wallet_by_id(db: Session, wallet_id: int):
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id, Wallet.deleted_at.is_(None)).first()
    if not wallet:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Wallet not found", "WALLET_NOT_FOUND")
    return wallet

def get_wallet_by_user_id(db: Session, user_id: int):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id, Wallet.deleted_at.is_(None)).first()
    if not wallet:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Wallet not found", "WALLET_NOT_FOUND")
    return wallet

def get_wallets(db: Session):
    return db.query(Wallet).filter(Wallet.deleted_at.is_(None)).all()

def top_up_wallet(db: Session, user_id: int, request: TopUpRequest):
    wallet = get_wallet_by_user_id(db, user_id)
    
    if request.amount <= 0:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Amount must be positive", "INVALID_AMOUNT")
        
    balance_before = wallet.balance
    wallet.balance += request.amount
    
    transaction = Transaction(
        user_id=user_id,
        wallet_id=wallet.id,
        type=TransactionType.TOP_UP,
        amount=request.amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        description="Top up via web interface"
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet

def adjust_wallet(db: Session, wallet_id: int, request: AdjustRequest):
    wallet = get_wallet_by_id(db, wallet_id)
    
    balance_before = wallet.balance
    
    if request.type == "ADD":
        if request.amount <= 0:
            raise CustomException(status.HTTP_400_BAD_REQUEST, "Amount must be positive", "INVALID_AMOUNT")
        wallet.balance += request.amount
    elif request.type == "SUBTRACT":
        if request.amount <= 0:
            raise CustomException(status.HTTP_400_BAD_REQUEST, "Amount must be positive", "INVALID_AMOUNT")
        if wallet.balance < request.amount:
            raise CustomException(status.HTTP_400_BAD_REQUEST, "Insufficient wallet balance", "INSUFFICIENT_BALANCE")
        wallet.balance -= request.amount
    else:
        wallet.balance = request.amount # Exact adjustment
        
    transaction = Transaction(
        user_id=wallet.user_id,
        wallet_id=wallet.id,
        type=TransactionType.ADJUSTMENT,
        amount=abs(wallet.balance - balance_before),
        balance_before=balance_before,
        balance_after=wallet.balance,
        description=f"Admin adjustment: {request.type}"
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet
