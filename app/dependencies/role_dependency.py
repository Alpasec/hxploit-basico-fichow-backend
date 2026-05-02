from fastapi import Depends
from app.models.user import User, RoleEnum
from app.dependencies.auth_dependency import get_current_user
from app.exceptions import forbidden

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise forbidden()
    return current_user
