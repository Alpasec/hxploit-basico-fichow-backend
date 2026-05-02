from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cart_schema import CartItemCreate, CartItemUpdate, CartValidateRequest
from app.services import cart_service
from app.utils.response import success_response
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("", response_model=None)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_details = cart_service.get_cart_details(db, current_user.id)
    return success_response(data=cart_details)

@router.post("/items", response_model=None)
def add_item_to_cart(item_data: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_service.add_item_to_cart(db, current_user.id, item_data)
    return success_response(message="Item added to cart")

@router.patch("/items/{cart_item_id}", response_model=None)
def update_cart_item(cart_item_id: int, item_data: CartItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_service.update_cart_item(db, current_user.id, cart_item_id, item_data)
    return success_response(message="Cart item updated")

@router.delete("/items/{cart_item_id}", response_model=None)
def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_service.delete_cart_item(db, current_user.id, cart_item_id)
    return success_response(message="Cart item removed")

@router.delete("/clear", response_model=None)
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_service.clear_cart(db, current_user.id)
    return success_response(message="Cart cleared")

@router.post("/validate", response_model=None)
def validate_cart(request: CartValidateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = cart_service.validate_cart(db, current_user.id, request.coupon_code)
    return success_response(data=result)
