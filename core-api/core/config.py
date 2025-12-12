"""
DeckBrain Core API - Configuration management.

This module handles configuration loading from environment variables
and provides a centralized settings object.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Reads from .env file if present, otherwise uses defaults.
    """
    
    # Application metadata
    app_name: str = "deckbrain-core-api"
    app_version: str = "0.2.0-dev"
    app_env: str = "development"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database configuration
    database_url: str = "sqlite:///./dev.db"
    # Switch to PostgreSQL by setting:
    # DATABASE_URL=postgresql://user:password@localhost:5432/deckbrain
    
    # CORS configuration
    cors_origins: str = "*"  # Comma-separated list
    # TODO: Restrict in production to dashboard domain
    
    # File storage
    storage_path: str = "./storage"  # Local path for uploaded files
    # TODO: Support cloud storage (S3, GCS) for production
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

