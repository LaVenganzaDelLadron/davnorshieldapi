"""Centralized application configuration loaded from the project `.env`."""

from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

from pydantic import AliasChoices, Field, field_validator
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
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "CyberShield DN"
    TIMEZONE: str = "Asia/Manila"

    # JWT
    SECRET_KEY: str = Field(default="change-me-in-production", min_length=8)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PostgreSQL
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/cybershield_dn",
        validation_alias=AliasChoices("DATABASE_URL", "DATABASE_SEURL"),
    )
    DATABASE_HOST: str = "postgres"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "cybershield_dn"

    # Firebase
    FIREBASE_PROJECT_ID: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FIREBASE_PROJECT_ID", "PROJECT_ID"),
    )
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIREBASE_API_KEY: str | None = Field(default=None, validation_alias=AliasChoices("FIREBASE_API_KEY", "API_KEY"))
    FIREBASE_AUTH_DOMAIN: str | None = Field(default=None, validation_alias=AliasChoices("FIREBASE_AUTH_DOMAIN", "AUTH_DOMAIN"))
    FIREBASE_STORAGE_BUCKET: str | None = Field(default=None, validation_alias=AliasChoices("FIREBASE_STORAGE_BUCKET", "STORAGE_BUCKET"))
    FIREBASE_MESSAGING_SENDER_ID: str | None = Field(default=None, validation_alias=AliasChoices("FIREBASE_MESSAGING_SENDER_ID", "MESSAGING_SENDER_ID"))
    FIREBASE_APP_ID: str | None = Field(default=None, validation_alias=AliasChoices("FIREBASE_APP_ID", "APP_ID"))
    FIREBASE_MEASUREMENT_ID: str | None = Field(default=None, validation_alias=AliasChoices("FIREBASE_MEASUREMENT_ID", "MEASUREMENT_ID"))

    # AI Engine
    AI_PROVIDER: str = Field(default="groq", validation_alias=AliasChoices("AI_PROVIDER"))
    AI_MODEL: str = Field(
        default="openai/gpt-oss-120b",
        validation_alias=AliasChoices("AI_MODEL", "GROQ_MODEL"),
    )
    AI_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("AI_API_KEY", "GROQ_API_KEY1"),
    )
    GROQ_API_KEYS: tuple[str, ...] = Field(
        default=(),
        validation_alias=AliasChoices("GROQ_API_KEYS"),
    )
    GROQ_API_KEY1: str | None = None
    GROQ_API_KEY2: str | None = None
    GROQ_API_KEY3: str | None = None
    GROQ_API_KEY4: str | None = None
    GROQ_API_KEY5: str | None = None
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_TIMEOUT: int = 120
    DEFAULT_MAX_CONTEXT_TOKENS: int = 6000
    DEFAULT_MAX_HISTORY_MESSAGES: int = 20
    DEFAULT_MAX_TOOL_OUTPUT_CHARS: int = 3000
    DEFAULT_MAX_FILE_SIZE: int = 10000
    DEFAULT_MAX_FILE_LIST_ITEMS: int = 50
    DEFAULT_MAX_OUTPUT_LINES: int = 100
    DEFAULT_RESERVE_RESPONSE_TOKENS: int = 1000
    THREAT_SCORE_THRESHOLD: float = 70.0
    AI_MIN_RISK_SCORE: float = 50.0
    AI_OUTBREAK_THRESHOLD: int = 10
    AI_SIMILARITY_THRESHOLD: float = 60.0

    # APScheduler
    OUTBREAK_INTERVAL_MINUTES: int = 10
    WEATHER_INTERVAL_HOURS: int = 24
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "Asia/Manila"
    NOTIFICATION_INTERVAL_SECONDS: int = 60
    CLEANUP_CRON_HOUR: int = 2
    ANALYTICS_INTERVAL_SECONDS: int = 3600

    # Uploads
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    @property
    def UPLOAD_DIR(self) -> str:
        """Backward-compatible alias for the configured upload directory."""

        return self.UPLOAD_DIRECTORY

    @property
    def REPORT_IMAGE_DIR(self) -> str:
        """Return the report image directory below the upload directory."""

        return f"{self.UPLOAD_DIRECTORY.rstrip('/')}/reports"

    @property
    def OUTBREAK_INTERVAL_SECONDS(self) -> int:
        """Backward-compatible interval in seconds for existing integrations."""

        return self.OUTBREAK_INTERVAL_MINUTES * 60

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
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return [str(origin).strip() for origin in value if str(origin).strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""

    return Settings()


settings = get_settings()
