from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_database_if_missing():
    url = make_url(settings.DATABASE_URL)
    database_name = url.database
    if not database_name:
        return

    if url.get_backend_name() != "postgresql":
        raise RuntimeError("Fichow backend is configured for PostgreSQL. Use a postgresql:// or postgresql+psycopg2:// DATABASE_URL.")

    server_url = url.set(database="postgres")
    server_engine = create_engine(server_url, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
    with server_engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
            {"database_name": database_name}
        ).scalar()
        if not exists:
            safe_database_name = database_name.replace('"', '""')
            connection.execute(text(f'CREATE DATABASE "{safe_database_name}"'))
    server_engine.dispose()

def create_tables_if_missing():
    import app.models
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
