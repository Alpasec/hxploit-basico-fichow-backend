from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductStockUpdate, ProductStatusUpdate
from app.exceptions import product_not_found

def get_products(db: Session, include_inactive: bool = False):
    query = db.query(Product).filter(Product.deleted_at.is_(None))
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    return query.all()

def get_product_by_id(db: Session, product_id: int, include_inactive: bool = False):
    query = db.query(Product).filter(Product.id == product_id, Product.deleted_at.is_(None))
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    product = query.first()
    if not product:
        raise product_not_found()
    return product

def create_product(db: Session, product_data: ProductCreate):
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product_id: int, product_data: ProductUpdate):
    product = get_product_by_id(db, product_id, include_inactive=True)
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

def update_product_stock(db: Session, product_id: int, stock_data: ProductStockUpdate):
    product = get_product_by_id(db, product_id, include_inactive=True)
    product.stock = stock_data.stock
    db.commit()
    db.refresh(product)
    return product

def update_product_status(db: Session, product_id: int, status_data: ProductStatusUpdate):
    product = get_product_by_id(db, product_id, include_inactive=True)
    product.is_active = status_data.is_active
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    from sqlalchemy.sql import func
    product = get_product_by_id(db, product_id, include_inactive=True)
    product.deleted_at = func.now()
    db.commit()
    return product
