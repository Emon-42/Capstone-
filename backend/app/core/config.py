import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Wedding Gift Ledger"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "wedding-gift-ledger-super-secure-secret-key-farhana-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # MySQL 8 default
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/wedding_gift_ledger?charset=utf8mb4"
    SQLITE_FALLBACK_URL: str = "sqlite:///./wedding_gift_ledger.db"

    # AI Integration
    AI_PROVIDER: str = "built-in-nlp"  # "gemini", "openai", "built-in-nlp"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Application Defaults
    FAMILY_NAME: str = "Farhana's Family"
    WEDDING_NAME: str = "Farhana & Tanvir's Wedding"
    WEDDING_DATE: str = "2026-11-20"
    DEFAULT_CURRENCY: str = "BDT"
    MESSAGE_SIGNATURE: str = "With love and warm regards,\nFarhana and Family"

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        extra = "allow"

settings = Settings()
