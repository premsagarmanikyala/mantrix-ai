"""
Configuration settings for the Mantrix application.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "Mantrix"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./mantrix.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI/ML settings
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = "mantrix.env"
        case_sensitive = True


settings = Settings()