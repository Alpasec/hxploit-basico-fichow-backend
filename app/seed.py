from decimal import Decimal
from sqlalchemy.orm import Session
from app.config import settings
from app.models.cart import Cart
from app.models.coupon import Coupon, DiscountType
from app.models.product import Product
from app.models.user import RoleEnum, User
from app.models.wallet import Wallet
from app.security import get_password_hash

CUSTOMERS = [
    ("Ana Customer", "ana@fichow.test"),
    ("Luis Customer", "luis@fichow.test"),
    ("Maria Customer", "maria@fichow.test"),
]

PRODUCTS = [
    ("Fichow clasico", "El clasico chaufa con pollo y huevo.", Decimal("15.00"), 100, "Platos Fuertes", "https://via.placeholder.com/400x300.png?text=Fichow+Clasico"),
    ("Fichow especial", "Chaufa con pollo, carne, chancho y langostinos.", Decimal("22.00"), 50, "Platos Fuertes", "https://via.placeholder.com/400x300.png?text=Fichow+Especial"),
    ("Fichow aeropuerto", "Chaufa mezclado con tallarin saltado.", Decimal("20.00"), 80, "Platos Fuertes", "https://via.placeholder.com/400x300.png?text=Fichow+Aeropuerto"),
    ("Fichow familiar", "Porcion gigante de Fichow clasico para toda la familia.", Decimal("45.00"), 30, "Para Compartir", "https://via.placeholder.com/400x300.png?text=Fichow+Familiar"),
    ("Wantan frito", "Porcion de 6 unidades de wantan frito con salsa de tamarindo.", Decimal("8.00"), 200, "Entradas", "https://via.placeholder.com/400x300.png?text=Wantan+Frito"),
    ("Inka Kola personal", "Gaseosa Inka Kola 500ml.", Decimal("4.00"), 300, "Bebidas", "https://via.placeholder.com/400x300.png?text=Inka+Kola"),
    ("Combo Fichow + bebida", "Un Fichow clasico mas una Inka Kola personal.", Decimal("18.00"), 150, "Combos", "https://via.placeholder.com/400x300.png?text=Combo+Fichow"),
    ("Combo familiar Fichow", "Un Fichow familiar, 12 wantanes y 1 gaseosa 1.5L.", Decimal("55.00"), 40, "Combos", "https://via.placeholder.com/400x300.png?text=Combo+Familiar"),
]

COUPONS = [
    ("FICHOW10", DiscountType.PERCENTAGE, Decimal("10.00"), 100, Decimal("20.00")),
    ("BIENVENIDO5", DiscountType.FIXED, Decimal("5.00"), 500, Decimal("15.00")),
    ("FAMILIAR15", DiscountType.PERCENTAGE, Decimal("15.00"), 50, Decimal("40.00")),
]

def seed_initial_data(db: Session):
    seed_users(db)
    seed_products(db)
    seed_coupons(db)
    db.commit()

def seed_users(db: Session):
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            full_name=settings.ADMIN_FULL_NAME,
            email=settings.ADMIN_EMAIL,
            password_hash=get_password_hash(settings.ADMIN_PASSWORD),
            role=RoleEnum.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.flush()
        ensure_wallet_and_cart(db, admin, Decimal("1000.00"))

    for full_name, email in CUSTOMERS:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                full_name=full_name,
                email=email,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role=RoleEnum.CUSTOMER,
                is_active=True,
            )
            db.add(user)
            db.flush()
        ensure_wallet_and_cart(db, user, Decimal(str(settings.DEFAULT_WALLET_BALANCE)))

def ensure_wallet_and_cart(db: Session, user: User, balance: Decimal):
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    if not wallet:
        db.add(Wallet(user_id=user.id, balance=balance, currency=settings.DEFAULT_CURRENCY))

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        db.add(Cart(user_id=user.id))

def seed_products(db: Session):
    for name, description, price, stock, category, image_url in PRODUCTS:
        product = db.query(Product).filter(Product.name == name).first()
        if not product:
            db.add(Product(
                name=name,
                description=description,
                price=price,
                stock=stock,
                category=category,
                image_url=image_url,
                is_active=True,
            ))

def seed_coupons(db: Session):
    for code, discount_type, discount_value, max_uses, min_purchase_amount in COUPONS:
        coupon = db.query(Coupon).filter(Coupon.code == code).first()
        if not coupon:
            db.add(Coupon(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                max_uses=max_uses,
                min_purchase_amount=min_purchase_amount,
                is_active=True,
            ))
