from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product_schema import ProductResponse, ProductCreate, ProductUpdate, ProductStockUpdate, ProductStatusUpdate
from app.services import product_service
from app.utils.response import success_response
from app.dependencies.role_dependency import get_admin_user
from app.dependencies.auth_dependency import get_current_user
from app.models.user import User

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", response_model=None)
def get_products(db: Session = Depends(get_db)):
    products = product_service.get_products(db, include_inactive=False)
    return success_response(data=[ProductResponse.model_validate(p).model_dump() for p in products])

@router.get("/all", response_model=None)
def get_all_products(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    products = product_service.get_products(db, include_inactive=True)
    return success_response(data=[ProductResponse.model_validate(p).model_dump() for p in products])

@router.get("/{product_id}", response_model=None)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)
    return success_response(data=ProductResponse.model_validate(product).model_dump())

@router.post("", response_model=None)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    product = product_service.create_product(db, product_data)
    return success_response(data=ProductResponse.model_validate(product).model_dump(), message="Product created successfully")

@router.patch("/{product_id}", response_model=None)
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    product = product_service.update_product(db, product_id, product_data)
    return success_response(data=ProductResponse.model_validate(product).model_dump(), message="Product updated successfully")

@router.delete("/{product_id}", response_model=None)
def delete_product(product_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    product_service.delete_product(db, product_id)
    return success_response(message="Product deleted successfully")

@router.patch("/{product_id}/stock", response_model=None)
def update_product_stock(product_id: int, stock_data: ProductStockUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    product = product_service.update_product_stock(db, product_id, stock_data)
    return success_response(data=ProductResponse.model_validate(product).model_dump(), message="Product stock updated")

@router.patch("/{product_id}/status", response_model=None)
def update_product_status(product_id: int, status_data: ProductStatusUpdate, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    product = product_service.update_product_status(db, product_id, status_data)
    return success_response(data=ProductResponse.model_validate(product).model_dump(), message="Product status updated")
