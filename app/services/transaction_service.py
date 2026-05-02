from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.exceptions import transaction_not_found

def get_transactions(db: Session, user_id: int = None):
    query = db.query(Transaction).filter(Transaction.deleted_at.is_(None))
    if user_id:
        query = query.filter(Transaction.user_id == user_id)
    return query.order_by(Transaction.created_at.desc()).all()

def get_transaction_by_id(db: Session, transaction_id: int):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.deleted_at.is_(None)).first()
    if not transaction:
        raise transaction_not_found()
    return transaction
