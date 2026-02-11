from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "MOZAIC"
    API_V1_STR: str = "/api/v1"
    
    # Defaults allow demo endpoints to run even if .env is missing.
    # For production, override via .env.
    DATABASE_URL: str = "sqlite+aiosqlite:///./mozaic_demo.db"
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 32-byte urlsafe base64 (Fernet). Override in .env for real deployments.
    ENCRYPTION_KEY: str = "mZpB0Qb5QY8m2m0ZcYHhE9VwHk4cYH8b9Q0mZpB0Qb4="
    
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Dev-only: allow creating account connections even if external test fails
    ALLOW_INSECURE_ACCOUNT_CONNECTIONS: bool = False

    # Demo-only: allow Grafana connection without validation
    MOZAIC_DEMO_ALLOW_GRAFANA: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()