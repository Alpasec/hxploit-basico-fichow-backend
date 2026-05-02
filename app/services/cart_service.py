from sqlalchemy.orm import Session
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.coupon import Coupon
from app.schemas.cart_schema import CartItemCreate, CartItemUpdate
from app.exceptions import CustomException, product_not_found, insufficient_stock, invalid_coupon
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import status

def normalize_quantity(value):
    if isinstance(value, str):
        return float(value) if "." in value else int(value)
    return value

def get_cart_by_user_id(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id, Cart.deleted_at.is_(None)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def get_cart_items(db: Session, cart_id: int):
    return db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.deleted_at.is_(None)).all()

def add_item_to_cart(db: Session, user_id: int, item_data: CartItemCreate):
    cart = get_cart_by_user_id(db, user_id)
    product = db.query(Product).filter(Product.id == item_data.product_id, Product.deleted_at.is_(None)).first()
    quantity = normalize_quantity(item_data.quantity)
    
    if not product:
        raise product_not_found()
    if not product.is_active:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Product is inactive", "PRODUCT_INACTIVE")
        
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product.id,
        CartItem.deleted_at.is_(None)
    ).first()
    
    new_quantity = quantity
    if existing_item:
        new_quantity += existing_item.quantity
        
    if existing_item:
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

def update_cart_item(db: Session, user_id: int, item_id: int, item_data: CartItemUpdate):
    cart = get_cart_by_user_id(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id, CartItem.deleted_at.is_(None)).first()
    if not item:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Cart item not found", "ITEM_NOT_FOUND")

    quantity = normalize_quantity(item_data.quantity)
    product = db.query(Product).filter(Product.id == item.product_id, Product.deleted_at.is_(None)).first()
    if not product:
        raise product_not_found()
    if not product.is_active:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Product is inactive", "PRODUCT_INACTIVE")
        
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item

def delete_cart_item(db: Session, user_id: int, item_id: int):
    from sqlalchemy.sql import func
    cart = get_cart_by_user_id(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id, CartItem.deleted_at.is_(None)).first()
    if not item:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Cart item not found", "ITEM_NOT_FOUND")
        
    item.deleted_at = func.now()
    db.commit()
    return True

def clear_cart(db: Session, user_id: int):
    from sqlalchemy.sql import func
    cart = get_cart_by_user_id(db, user_id)
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.deleted_at.is_(None)).all()
    for item in items:
        item.deleted_at = func.now()
    db.commit()
    return True

def get_cart_details(db: Session, user_id: int):
    cart = get_cart_by_user_id(db, user_id)
    items = get_cart_items(db, cart.id)
    
    total = Decimal("0.00")
    items_data = []
    
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.deleted_at.is_(None)).first()
        if product:
            subtotal = product.price * item.quantity
            total += subtotal
            items_data.append({
                "id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock,
                    "category": product.category,
                    "image_url": product.image_url,
                    "is_active": product.is_active,
                    "created_at": product.created_at,
                },
                "subtotal": subtotal
            })
            
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items_data,
        "total": total
    }

def validate_cart(db: Session, user_id: int, coupon_code: str = None):
    cart = get_cart_by_user_id(db, user_id)
    items = get_cart_items(db, cart.id)
    
    if not items:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Cart is empty", "EMPTY_CART")

    subtotal = Decimal("0.00")
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.deleted_at.is_(None)).first()
        if not product:
            raise product_not_found()
        if not product.is_active:
            raise CustomException(status.HTTP_400_BAD_REQUEST, "Product is inactive", "PRODUCT_INACTIVE")
        subtotal += product.price * item.quantity

    cart_details = get_cart_details(db, user_id)
    discount = Decimal("0.00")
    if coupon_code:
        coupon = db.query(Coupon).filter(Coupon.code == coupon_code.strip().upper(), Coupon.deleted_at.is_(None)).first()
        if not coupon:
            raise invalid_coupon()
        if not coupon.is_active:
            raise invalid_coupon()
        if coupon.expires_at and coupon.expires_at < datetime.now():
            raise invalid_coupon()
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            raise invalid_coupon()
        if subtotal < coupon.min_purchase_amount:
            raise invalid_coupon()
            
        if coupon.discount_type.value == "PERCENTAGE":
            discount = subtotal * (coupon.discount_value / Decimal("100"))
        else:
            discount = coupon.discount_value
            
        if discount > subtotal:
            discount = subtotal
            
    return {
        "cart": cart_details,
        "subtotal": subtotal,
        "discount": discount,
        "total": subtotal - discount,
        "coupon_valid": bool(coupon_code and discount > 0)
    }
