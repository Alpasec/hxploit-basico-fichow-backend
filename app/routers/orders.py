from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order_schema import OrderResponse, OrderCreate, OrderStatusUpdate
from app.services import order_service
from app.utils.response import success_response
from app.dependencies.role_dependency import get_admin_user
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User
from app.exceptions import forbidden

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=None)
def create_order(request: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = order_service.create_order(db, current_user.id, request)
    return success_response(data=OrderResponse.model_validate(order).model_dump(), message="Order created successfully")

@router.get("/me", response_model=None)
def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = order_service.get_orders(db, user_id=current_user.id)
    return success_response(data=[OrderResponse.model_validate(o).model_dump() for o in orders])

@router.get("/{order_id}", response_model=None)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = order_service.get_order_by_id(db, order_id)
    if current_user.role.value != "ADMIN" and order.user_id != current_user.id:
        raise forbidden()
    return success_response(data=OrderResponse.model_validate(order).model_dump())

@router.get("", response_model=None)
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = order_service.get_orders(db)
    return success_response(data=[OrderResponse.model_validate(o).model_dump() for o in orders])

@router.patch("/{order_id}/status", response_model=None)
def update_order_status(order_id: int, status_data: OrderStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    order = order_service.update_order_status(db, order_id, status_data)
    return success_response(data=OrderResponse.model_validate(order).model_dump(), message="Order status updated")

@router.post("/{order_id}/cancel", response_model=None)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = order_service.cancel_order(db, current_user.id, order_id, current_user.role.value == "ADMIN")
    return success_response(data=OrderResponse.model_validate(order).model_dump(), message="Order cancelled successfully")

@router.post("/{order_id}/refund", response_model=None)
def refund_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = order_service.refund_order(db, order_id)
    return success_response(data=OrderResponse.model_validate(order).model_dump(), message="Order refunded successfully")
