from sqlalchemy.orm import Session
from app.models.coupon import Coupon
from app.schemas.coupon_schema import CouponCreate, CouponUpdate, CouponStatusUpdate, CouponValidateRequest
from app.exceptions import CustomException, invalid_coupon
from datetime import datetime
from decimal import Decimal
from fastapi import status

def get_coupons(db: Session):
    return db.query(Coupon).filter(Coupon.deleted_at.is_(None)).all()

def get_coupon_by_id(db: Session, coupon_id: int):
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id, Coupon.deleted_at.is_(None)).first()
    if not coupon:
        raise CustomException(status.HTTP_404_NOT_FOUND, "Coupon not found", "COUPON_NOT_FOUND")
    return coupon

def create_coupon(db: Session, coupon_data: CouponCreate):
    coupon_data.code = coupon_data.code.strip().upper()
    existing = db.query(Coupon).filter(Coupon.code == coupon_data.code, Coupon.deleted_at.is_(None)).first()
    if existing:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Coupon code already exists", "COUPON_EXISTS")
        
    coupon = Coupon(**coupon_data.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon

def update_coupon(db: Session, coupon_id: int, coupon_data: CouponUpdate):
    coupon = get_coupon_by_id(db, coupon_id)
    update_data = coupon_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(coupon, key, value)
    db.commit()
    db.refresh(coupon)
    return coupon

def update_coupon_status(db: Session, coupon_id: int, status_data: CouponStatusUpdate):
    coupon = get_coupon_by_id(db, coupon_id)
    coupon.is_active = status_data.is_active
    db.commit()
    db.refresh(coupon)
    return coupon

def delete_coupon(db: Session, coupon_id: int):
    from sqlalchemy.sql import func
    coupon = get_coupon_by_id(db, coupon_id)
    coupon.deleted_at = func.now()
    db.commit()
    return coupon

def validate_coupon(db: Session, request: CouponValidateRequest):
    coupon = db.query(Coupon).filter(Coupon.code == request.code.strip().upper(), Coupon.deleted_at.is_(None)).first()
    if not coupon:
        raise invalid_coupon()
    if not coupon.is_active:
        raise invalid_coupon()
    if coupon.expires_at and coupon.expires_at < datetime.now():
        raise invalid_coupon()
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        raise invalid_coupon()
    if request.subtotal < coupon.min_purchase_amount:
        raise invalid_coupon()
        
    discount = Decimal("0.00")
    if coupon.discount_type.value == "PERCENTAGE":
        discount = request.subtotal * (coupon.discount_value / Decimal("100"))
    else:
        discount = coupon.discount_value
        
    if discount > request.subtotal:
        discount = request.subtotal
        
    return {
        "is_valid": True,
        "discount_amount": discount,
        "coupon_id": coupon.id
    }
