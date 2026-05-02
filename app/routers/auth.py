import ast
import json
import re
from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.schemas.auth_schema import UserRegister, UserLogin, Token
from app.services import auth_service
from app.utils.response import success_response
from app.dependencies.auth_dependency import get_current_user
from app.exceptions import CustomException
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(request: Request, db: Session = Depends(get_db)):
    user_data = validate_request_model(UserRegister, await parse_request_data(request))
    auth_service.register_user(db, user_data)
    return success_response(message="User registered successfully")

@router.post("/login")
async def login(request: Request, response: Response, db: Session = Depends(get_db)):
    user_data = validate_request_model(UserLogin, await parse_request_data(request))
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

async def parse_request_data(request: Request) -> dict:
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form = await request.form()
            data = dict(form)
            if "username" in data and "email" not in data:
                data["email"] = data["username"]
            return data

        body = await request.body()
        if not body:
            return {}

        raw_body = body.decode("utf-8").strip()
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            try:
                data = ast.literal_eval(raw_body)
            except (ValueError, SyntaxError):
                data = parse_loose_body(raw_body)

        if isinstance(data, dict):
            return data
    except (ValueError, SyntaxError, ValidationError):
        pass

    raise CustomException(status.HTTP_400_BAD_REQUEST, "Invalid request data", "VALIDATION_ERROR")

def validate_request_model(model, data: dict):
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise CustomException(status.HTTP_400_BAD_REQUEST, format_validation_error(exc), "VALIDATION_ERROR")

def parse_loose_body(raw_body: str) -> dict:
    data = {}
    for key in ["full_name", "email", "username", "password"]:
        match = re.search(rf"{key}\\?['\"]?\s*[:=]\s*\\?['\"]?([^,}}'\"&]+)", raw_body)
        if match:
            data[key] = match.group(1).strip()
    if "username" in data and "email" not in data:
        data["email"] = data["username"]
    return data

def format_validation_error(exc: ValidationError) -> str:
    first_error = exc.errors()[0] if exc.errors() else {}
    field = first_error.get("loc", ["request"])[-1]
    error_type = first_error.get("type", "")
    context = first_error.get("ctx", {})

    if error_type == "string_too_short":
        return f"{field} must have at least {context.get('min_length', 'the required')} characters"
    if error_type == "string_too_long":
        return f"{field} is too long"
    if error_type == "value_error":
        return f"{field} is invalid"
    if error_type == "missing":
        return f"{field} is required"

    return first_error.get("msg", "Invalid request data")
