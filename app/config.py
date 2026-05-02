from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Fichow API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    API_PREFIX: str = "/api/v1"
    
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    DATABASE_URL: str
    AUTO_CREATE_DATABASE: bool = True
    AUTO_CREATE_TABLES: bool = True
    AUTO_SEED_DATA: bool = True
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    DEFAULT_USER_ROLE: str = "CUSTOMER"
    DEFAULT_WALLET_BALANCE: float = 100.00
    DEFAULT_CURRENCY: str = "PEN"
    
    ADMIN_EMAIL: str = "admin@fichow.test"
    ADMIN_PASSWORD: str = "Admin123"
    ADMIN_FULL_NAME: str = "Fichow Admin"
    
    ENABLE_DOCS: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def get_allowed_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
