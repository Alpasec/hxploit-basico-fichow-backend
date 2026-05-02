from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.schemas.auth_schema import UserRegister, UserLogin, Token
from app.services import auth_service
from app.utils.response import success_response
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    auth_service.register_user(db, user_data)
    return success_response(message="User registered successfully")

@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    result = auth_service.login_user(db, user_data)
    response.set_cookie(
        key=settings.JWT_COOKIE_NAME,
        value=result["access_token"],
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )
    result.pop("access_token", None)
    return success_response(data=result, message="Login successful")

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(data={
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }, message="Current user info retrieved")

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key=settings.JWT_COOKIE_NAME,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )
    return success_response(message="Logged out successfully")
