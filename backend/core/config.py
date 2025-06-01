"""
Configuration management for the application.
This module handles:
- Environment variable loading and validation
- Application configuration settings
- Database configuration
- API keys and secrets management
- Environment-specific settings (development, production, testing)
"""

import os
from typing import Optional, List
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Flask Configuration
    PORT: int = 5000
    FLASK_ENV: str = "development"
    DEBUG: bool = False
    TESTING: bool = False
    BASE_URL: str = os.getenv("BASE_URL")
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_API_KEY: str
    SUPABASE_JWT_SECRET: str
    
    # Email Configuration
    SKIP_EMAIL_CONFIRMATION: bool = False
    PRE_AUTHORIZED_EMAILS: List[str] = []
    
    # API Keys
    OPENAI_API_KEY: str
    GROQ_BASE_URL: str
    GROQ_API_KEY: str
    JWT_SECRET_KEY: str
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT: str = "200 per day"
    
    @field_validator("SKIP_EMAIL_CONFIRMATION", mode="before")
    def set_skip_email_confirmation(cls, v, info):
        return v if v is not None else info.data.get("FLASK_ENV") == "development"
    
    @field_validator("FLASK_ENV")
    def validate_flask_env(cls, v):
        allowed_envs = ["development", "production", "testing"]
        if v not in allowed_envs:
            raise ValueError(f"FLASK_ENV must be one of {allowed_envs}")
        return v
    
    @field_validator("CORS_ORIGINS")
    def parse_cors_origins(cls, v):
        return [origin.strip() for origin in v.split(",")] if isinstance(v, str) else v
    
    @field_validator("PRE_AUTHORIZED_EMAILS")
    def parse_pre_authorized_emails(cls, v):
        return [email.strip() for email in v.split(",")] if isinstance(v, str) else v
    
    @field_validator("BASE_URL")
    def validate_base_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("BASE_URL must start with http:// or https://")
        return v.rstrip("/")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

# Create a global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the application settings."""
    return settings 