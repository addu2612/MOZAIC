from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "MOZAIC"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ENCRYPTION_KEY: str
    
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Dev-only: allow creating account connections even if external test fails
    ALLOW_INSECURE_ACCOUNT_CONNECTIONS: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()