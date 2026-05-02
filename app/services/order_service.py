from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import func
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.wallet import Wallet
from app.models.transaction import Transaction, TransactionType
from app.models.coupon import Coupon, CouponUsage
from app.models.cart import CartItem
from app.schemas.order_schema import OrderCreate, OrderStatusUpdate
from app.services.cart_service import validate_cart
from app.exceptions import CustomException, order_not_found, insufficient_balance, empty_cart, product_not_found, insufficient_stock
from fastapi import status

def get_orders(db: Session, user_id: int = None):
    query = db.query(Order).options(selectinload(Order.items)).filter(Order.deleted_at.is_(None))
    if user_id:
        query = query.filter(Order.user_id == user_id)
    return query.order_by(Order.created_at.desc()).all()

def get_order_by_id(db: Session, order_id: int):
    order = db.query(Order).options(selectinload(Order.items)).filter(Order.id == order_id, Order.deleted_at.is_(None)).first()
    if not order:
        raise order_not_found()
    return order

def create_order(db: Session, user_id: int, request: OrderCreate):
    try:
        validation = validate_cart(db, user_id, request.coupon_code)
        cart_details = validation["cart"]
        
        if not cart_details["items"]:
            raise empty_cart()
            
        total_amount = validation["total"]
        
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id, Wallet.deleted_at.is_(None)).first()
        if not wallet or wallet.balance < total_amount:
            raise insufficient_balance()

        coupon_id = None
        if validation["coupon_valid"] and request.coupon_code:
            coupon = db.query(Coupon).filter(
                Coupon.code == request.coupon_code.strip().upper(),
                Coupon.deleted_at.is_(None),
                Coupon.is_active == True,
            ).first()
            if coupon:
                coupon_id = coupon.id
                coupon.used_count += 1
                db.add(coupon)

        order = Order(
            user_id=user_id,
            coupon_id=coupon_id,
            subtotal=validation["subtotal"],
            discount_amount=validation["discount"],
            total_amount=total_amount,
            status=OrderStatus.PAID
        )
        db.add(order)
        db.flush()
        
        cart_item_ids = []
        for item in cart_details["items"]:
            product = db.query(Product).filter(Product.id == item["product_id"], Product.deleted_at.is_(None)).first()
            if not product:
                raise product_not_found()
            if not product.is_active:
                raise CustomException(status.HTTP_400_BAD_REQUEST, "Product is inactive", "PRODUCT_INACTIVE")
            item_subtotal = product.price * item["quantity"]
            product.stock -= item["quantity"]
            db.add(product)
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                quantity=item["quantity"],
                unit_price=product.price,
                subtotal=item_subtotal
            )
            db.add(order_item)
            cart_item_ids.append(item["id"])
            
        balance_before = wallet.balance
        wallet.balance -= total_amount
        db.add(wallet)
        
        transaction = Transaction(
            user_id=user_id,
            wallet_id=wallet.id,
            order_id=order.id,
            type=TransactionType.PURCHASE,
            amount=total_amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=f"Payment for order #{order.id}"
        )
        db.add(transaction)
        
        if coupon_id:
            coupon_usage = CouponUsage(
                coupon_id=coupon_id,
                user_id=user_id,
                order_id=order.id
            )
            db.add(coupon_usage)

        if cart_item_ids:
            db.query(CartItem).filter(CartItem.id.in_(cart_item_ids)).update(
                {CartItem.deleted_at: func.now()},
                synchronize_session=False
            )
            
        db.commit()
        return get_order_by_id(db, order.id)
    except Exception:
        db.rollback()
        raise

def update_order_status(db: Session, order_id: int, status_data: OrderStatusUpdate):
    order = get_order_by_id(db, order_id)
    if order.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Order status cannot be changed", "INVALID_STATUS")
    if status_data.status in [OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Use the cancel or refund endpoint", "INVALID_STATUS")
    order.status = status_data.status
    db.commit()
    db.refresh(order)
    return order

def _restore_order_stock(db: Session, order: Order):
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.deleted_at.is_(None)).first()
        if product:
            product.stock += item.quantity
            db.add(product)

def _decrease_coupon_usage(db: Session, order: Order):
    if order.coupon_id:
        coupon = db.query(Coupon).filter(Coupon.id == order.coupon_id, Coupon.deleted_at.is_(None)).first()
        if coupon and coupon.used_count > 0:
            coupon.used_count -= 1
            db.add(coupon)

def cancel_order(db: Session, user_id: int, order_id: int, is_admin: bool = False):
    order = get_order_by_id(db, order_id)
    if order.status != OrderStatus.CREATED and order.status != OrderStatus.PAID:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Order cannot be cancelled", "INVALID_STATUS")
        
    try:
        original_status = order.status
        if original_status == OrderStatus.PAID:
            wallet = db.query(Wallet).filter(Wallet.user_id == order.user_id, Wallet.deleted_at.is_(None)).first()
            if not wallet:
                raise insufficient_balance()
            balance_before = wallet.balance
            wallet.balance += order.total_amount
            
            transaction = Transaction(
                user_id=order.user_id,
                wallet_id=wallet.id,
                order_id=order.id,
                type=TransactionType.REFUND,
                amount=order.total_amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=f"Refund for cancelled order #{order.id}"
            )
            db.add(wallet)
            db.add(transaction)
            _restore_order_stock(db, order)
            _decrease_coupon_usage(db, order)
            order.status = OrderStatus.REFUNDED
        else:
            order.status = OrderStatus.CANCELLED
            
        db.commit()
        return get_order_by_id(db, order.id)
    except Exception:
        db.rollback()
        raise

def refund_order(db: Session, order_id: int):
    order = get_order_by_id(db, order_id)
    if order.status == OrderStatus.REFUNDED or order.status == OrderStatus.CANCELLED:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Order already refunded or cancelled", "INVALID_STATUS")
    if order.status not in [OrderStatus.PAID, OrderStatus.DELIVERED]:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Order cannot be refunded", "INVALID_STATUS")
        
    try:
        order.status = OrderStatus.REFUNDED
        
        wallet = db.query(Wallet).filter(Wallet.user_id == order.user_id, Wallet.deleted_at.is_(None)).first()
        if not wallet:
            raise insufficient_balance()
        balance_before = wallet.balance
        wallet.balance += order.total_amount
        
        transaction = Transaction(
            user_id=order.user_id,
            wallet_id=wallet.id,
            order_id=order.id,
            type=TransactionType.REFUND,
            amount=order.total_amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            description=f"Admin refund for order #{order.id}"
        )
        db.add(wallet)
        db.add(transaction)
        _restore_order_stock(db, order)
        _decrease_coupon_usage(db, order)
        db.commit()
        return get_order_by_id(db, order.id)
    except Exception:
        db.rollback()
        raise
