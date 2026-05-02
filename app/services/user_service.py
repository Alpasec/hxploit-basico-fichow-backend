from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserUpdate, UserStatusUpdate, UserRoleUpdate
from app.exceptions import user_not_found

def get_users(db: Session):
    return db.query(User).filter(User.deleted_at.is_(None)).all()

def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise user_not_found()
    return user

def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = get_user_by_id(db, user_id)
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def update_user_status(db: Session, user_id: int, status_data: UserStatusUpdate):
    user = get_user_by_id(db, user_id)
    user.is_active = status_data.is_active
    db.commit()
    db.refresh(user)
    return user

def update_user_role(db: Session, user_id: int, role_data: UserRoleUpdate):
    user = get_user_by_id(db, user_id)
    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user
