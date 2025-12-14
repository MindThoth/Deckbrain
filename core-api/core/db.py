"""
DeckBrain Core API - Database connection and session management.

This module handles SQLAlchemy engine and session setup.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings

# Database URL from configuration
database_url = settings.database_url

# Create SQLAlchemy engine
# For SQLite, we need check_same_thread=False for FastAPI
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    echo=True if settings.app_env == "development" else False,
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.
    
    Yields a database session and ensures it's closed after use.
    
    Usage in FastAPI endpoints:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    
    Creates all tables defined in models.
    Should be called during application startup or via migrations.
    """
    # Import all models to register them with Base
    import core.models  # noqa: F401
    
    Base.metadata.create_all(bind=engine)


def check_db_initialized() -> None:
    """
    Check if database tables exist.
    
    Raises RuntimeError if the 'devices' table is missing,
    indicating migrations have not been applied.
    
    This is called at application startup to fail fast with a clear error.
    """
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "devices" not in tables:
        raise RuntimeError(
            "Database not initialized. Required tables are missing.\n"
            "Please run migrations: alembic upgrade head"
        )

