from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.utils.response import success_response
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.wallet import Wallet
from app.models.transaction import Transaction

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/summary", response_model=None)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_users = db.query(User).filter(User.deleted_at.is_(None)).count()
    total_products = db.query(Product).filter(Product.deleted_at.is_(None)).count()
    total_orders = db.query(Order).filter(Order.deleted_at.is_(None)).count()
    total_transactions = db.query(Transaction).filter(Transaction.deleted_at.is_(None)).count()
    total_wallet_balance = db.query(func.sum(Wallet.balance)).filter(Wallet.deleted_at.is_(None)).scalar() or 0.00
    total_sales = db.query(func.sum(Order.total_amount)).filter(
        Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]),
        Order.deleted_at.is_(None)
    ).scalar() or 0.00
    
    return success_response(data={
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_transactions": total_transactions,
        "total_wallet_balance": float(total_wallet_balance),
        "total_sales": float(total_sales)
    })

@router.get("/sales-report", response_model=None)
def get_sales_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]), Order.deleted_at.is_(None)).all()
    total = sum([o.total_amount for o in orders])
    return success_response(data={"count": len(orders), "total_revenue": float(total)})

@router.get("/users-report", response_model=None)
def get_users_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    active = db.query(User).filter(User.is_active == True, User.deleted_at.is_(None)).count()
    inactive = db.query(User).filter(User.is_active == False, User.deleted_at.is_(None)).count()
    return success_response(data={"active_users": active, "inactive_users": inactive})

@router.get("/products-report", response_model=None)
def get_products_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_stock = db.query(func.sum(Product.stock)).filter(Product.deleted_at.is_(None)).scalar() or 0
    active_products = db.query(Product).filter(Product.is_active == True, Product.deleted_at.is_(None)).count()
    return success_response(data={"total_stock_items": int(total_stock), "active_products": active_products})
