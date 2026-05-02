from app.config import settings
from app.database import SessionLocal, create_database_if_missing, create_tables_if_missing
from app.seed import seed_initial_data

def initialize_application():
    if settings.AUTO_CREATE_DATABASE:
        create_database_if_missing()

    if settings.AUTO_CREATE_TABLES:
        create_tables_if_missing()

    if settings.AUTO_SEED_DATA:
        db = SessionLocal()
        try:
            seed_initial_data(db)
        finally:
            db.close()
