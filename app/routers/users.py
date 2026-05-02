from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user_schema import UserResponse, UserUpdate, UserStatusUpdate, UserRoleUpdate
from app.services import user_service
from app.utils.response import success_response
from app.dependencies.auth_dependency import get_current_user
from app.dependencies.role_dependency import get_admin_user
from app.models.user import User
from app.exceptions import forbidden

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=None)
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = user_service.get_users(db)
    return success_response(data=[UserResponse.model_validate(u).model_dump() for u in users])

@router.get("/{user_id}", response_model=None)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value != "ADMIN" and current_user.id != user_id:
        raise forbidden()
    user = user_service.get_user_by_id(db, user_id)
    return success_response(data=UserResponse.model_validate(user).model_dump())

@router.patch("/{user_id}", response_model=None)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value != "ADMIN" and current_user.id != user_id:
        raise forbidden()
    user = user_service.update_user(db, user_id, user_data)
    return success_response(data=UserResponse.model_validate(user).model_dump(), message="User updated successfully")

@router.patch("/{user_id}/status", response_model=None)
def update_user_status(user_id: int, status_data: UserStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    user = user_service.update_user_status(db, user_id, status_data)
    return success_response(data=UserResponse.model_validate(user).model_dump(), message="User status updated")

@router.patch("/{user_id}/role", response_model=None)
def update_user_role(user_id: int, role_data: UserRoleUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    user = user_service.update_user_role(db, user_id, role_data)
    return success_response(data=UserResponse.model_validate(user).model_dump(), message="User role updated")
