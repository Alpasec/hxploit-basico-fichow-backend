from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.models.wallet import Wallet
from app.models.cart import Cart
from app.schemas.auth_schema import UserRegister, UserLogin
from app.security import get_password_hash, verify_password, create_access_token
from app.config import settings
from app.exceptions import CustomException, invalid_credentials
from fastapi import status

def register_user(db: Session, user_data: UserRegister):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise CustomException(status.HTTP_400_BAD_REQUEST, "Email already registered", "EMAIL_REGISTERED")
        
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password,
        role=RoleEnum(settings.DEFAULT_USER_ROLE),
        is_active=True
    )
    db.add(new_user)
    db.flush() # to get new_user.id
    
    new_wallet = Wallet(
        user_id=new_user.id,
        balance=settings.DEFAULT_WALLET_BALANCE,
        currency=settings.DEFAULT_CURRENCY
    )
    db.add(new_wallet)
    
    new_cart = Cart(user_id=new_user.id)
    db.add(new_cart)
    
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, user_data: UserLogin):
    user = db.query(User).filter(User.email == user_data.email, User.deleted_at.is_(None)).first()
    if not user:
        raise CustomException(status.HTTP_404_NOT_FOUND, "User not found", "USER_NOT_FOUND")
        
    if not verify_password(user_data.password, user.password_hash):
        raise CustomException(status.HTTP_401_UNAUTHORIZED, "Invalid password", "INVALID_PASSWORD")
        
    if not user.is_active:
        raise CustomException(status.HTTP_403_FORBIDDEN, "User is inactive", "USER_INACTIVE")
        
    access_token = create_access_token(
        data={"sub": str(user.id), "user_id": user.id, "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.value
        }
    }
