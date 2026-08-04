"""
Application configuration loaded from .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Agrilux application settings — all values come from .env"""

    JWT_SECRET: str = "change-me-in-production"
    JWT_EXPIRE_MINUTES: int = 60
    DB_URL: str = "sqlite:///./agrilux.db"
    CORS_ORIGIN: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
