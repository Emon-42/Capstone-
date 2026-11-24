import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

def get_engine():
    try:
        # Try primary MySQL database
        primary_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        # Test connection
        with primary_engine.connect() as conn:
            logger.info("Successfully connected to MySQL database: %s", settings.DATABASE_URL.split("@")[-1])
        return primary_engine, "MySQL"
    except Exception as e:
        logger.warning(
            "Primary MySQL connection failed (%s). Falling back to SQLite: %s",
            e,
            settings.SQLITE_FALLBACK_URL
        )
        fallback_engine = create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
        return fallback_engine, "SQLite"

engine, DB_ENGINE_TYPE = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
