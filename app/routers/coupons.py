from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.coupon_schema import CouponResponse, CouponCreate, CouponUpdate, CouponStatusUpdate, CouponValidateRequest
from app.services import coupon_service
from app.utils.response import success_response
from app.dependencies.role_dependency import get_admin_user
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User

router = APIRouter(prefix="/coupons", tags=["coupons"])

@router.get("", response_model=None)
def get_coupons(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    coupons = coupon_service.get_coupons(db)
    return success_response(data=[CouponResponse.model_validate(c).model_dump() for c in coupons])

@router.get("/{coupon_id}", response_model=None)
def get_coupon(coupon_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    coupon = coupon_service.get_coupon_by_id(db, coupon_id)
    return success_response(data=CouponResponse.model_validate(coupon).model_dump())

@router.post("", response_model=None)
def create_coupon(coupon_data: CouponCreate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    coupon = coupon_service.create_coupon(db, coupon_data)
    return success_response(data=CouponResponse.model_validate(coupon).model_dump(), message="Coupon created successfully")

@router.patch("/{coupon_id}", response_model=None)
def update_coupon(coupon_id: int, coupon_data: CouponUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    coupon = coupon_service.update_coupon(db, coupon_id, coupon_data)
    return success_response(data=CouponResponse.model_validate(coupon).model_dump(), message="Coupon updated successfully")

@router.delete("/{coupon_id}", response_model=None)
def delete_coupon(coupon_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    coupon_service.delete_coupon(db, coupon_id)
    return success_response(message="Coupon deleted successfully")

@router.patch("/{coupon_id}/status", response_model=None)
def update_coupon_status(coupon_id: int, status_data: CouponStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    coupon = coupon_service.update_coupon_status(db, coupon_id, status_data)
    return success_response(data=CouponResponse.model_validate(coupon).model_dump(), message="Coupon status updated")

@router.post("/validate", response_model=None)
def validate_coupon(request: CouponValidateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = coupon_service.validate_coupon(db, request)
    return success_response(data=result, message="Coupon is valid")
