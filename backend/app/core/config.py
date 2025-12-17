import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/lifecandle")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_BASE_URL: str = os.getenv("GEMINI_BASE_URL")
    GEMINI_MODEL_NAME:str = os.getenv("GEMINI_MODEL_NAME")
    class Config:
        env_file = ".env"

settings = Settings()
