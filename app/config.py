"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings sourced from `.env` and process environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "CyberShield DN API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    PROJECT_NAME: str = "CyberShield DN"
    TIMEZONE: str = "Asia/Manila"

    # JWT
    SECRET_KEY: str = Field(default="change-me-in-production", min_length=8)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/cybershield_dn"
    DATABASE_HOST: str = "postgres"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "cybershield_dn"

    # Firebase
    FIREBASE_PROJECT_ID: str | None = None
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # AI Engine
    AI_MIN_RISK_SCORE: float = 50.0
    AI_OUTBREAK_THRESHOLD: int = 10
    AI_SIMILARITY_THRESHOLD: float = 60.0

    # APScheduler
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "Asia/Manila"
    CYBER_WEATHER_CRON_HOUR: int = 6
    CYBER_WEATHER_CRON_MINUTE: int = 0
    OUTBREAK_INTERVAL_SECONDS: int = 600
    NOTIFICATION_INTERVAL_SECONDS: int = 60
    CLEANUP_CRON_HOUR: int = 2
    ANALYTICS_INTERVAL_SECONDS: int = 3600

    # Uploads
    UPLOAD_DIR: str = "uploads"
    REPORT_IMAGE_DIR: str = "uploads/reports"
    MAX_UPLOAD_SIZE_MB: int = 10

    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> list[str]:
        """Accept JSON-like lists or comma-separated strings."""

        if value is None:
            return []
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return [str(origin).strip() for origin in value if str(origin).strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""

    return Settings()


settings = get_settings()

