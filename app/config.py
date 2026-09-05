"""Centralized application configuration loaded from the project `.env`."""

from __future__ import annotations

import os
from functools import lru_cache
import json
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit
from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()



class Settings(BaseSettings):
    """Typed application settings sourced from `.env` and process environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME = os.getenv("APP_NAME")
    APP_VERSION = os.getenv("APP_VERSION")
    API_V1_PREFIX = os.getenv("API_V1_PREFIX")
    DEBUG = os.getenv("DEBUG")
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    PROJECT_NAME: str = "DavnorShield"
    TIMEZONE: str = "Asia/Manila"

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

    # PostgreSQL
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATABASE_HOST: str = "postgres"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "tagumshieldapi"

    # Firebase
    FIREBASE_PROJECT_ID = os.getenv("PROJECT_ID")
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIREBASE_API_KEY = os.getenv("API_KEY")
    FIREBASE_AUTH_DOMAIN = os.getenv("AUTH_DOMAIN")
    FIREBASE_STORAGE_BUCKET = os.getenv("STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID = os.getenv("MESSAGING_SENDER_ID")
    FIREBASE_APP_ID = os.getenv("APP_ID")
    FIREBASE_MEASUREMENT_ID = os.getenv("MEASUREMENT_ID")

    # AI Engine
    AI_PROVIDER: str = Field(default="groq", validation_alias=AliasChoices("AI_PROVIDER"))
    AI_MODEL = os.getenv("GROQ_MODEL")
    AI_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("AI_API_KEY", "GROQ_API_KEY1"),
    )
    GROQ_API_KEYS: tuple[str, ...] = Field(
        default=(),
        validation_alias=AliasChoices("GROQ_API_KEYS"),
    )
    GROQ_API_KEY1 = os.getenv("GROQ_API_KEY1")
    GROQ_API_KEY2 = os.getenv("GROQ_API_KEY2")
    GROQ_API_KEY3 = os.getenv("GROQ_API_KEY3")
    GROQ_API_KEY4 = os.getenv("GROQ_API_KEY4")
    GROQ_API_KEY5 = os.getenv("GROQ_API_KEY5")
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

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        """Normalize legacy PostgreSQL URLs using the typed database settings."""

        parsed = urlsplit(self.DATABASE_URL)
        if parsed.scheme not in {"postgresql", "postgresql+asyncpg"}:
            return self

        host = parsed.hostname or self.DATABASE_HOST
        port = parsed.port or self.DATABASE_PORT
        username = quote(parsed.username or self.DATABASE_USER, safe="")
        password = quote(parsed.password or self.DATABASE_PASSWORD, safe="")
        database = parsed.path.lstrip("/") or self.DATABASE_NAME
        query = parsed.query
        self.DATABASE_URL = urlunsplit(
            (
                "postgresql+asyncpg",
                f"{username}:{password}@{host}:{port}",
                f"/{database}",
                query,
                parsed.fragment,
            )
        )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""

    return Settings()


settings = get_settings()
