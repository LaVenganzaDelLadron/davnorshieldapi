"""Centralized application configuration using os.getenv()."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from urllib.parse import quote, urlsplit, urlunsplit

from dotenv import load_dotenv

# Load .env into environment variables
load_dotenv()


class Settings:
    def __init__(self):
        # =========================
        # Application
        # =========================
        self.APP_NAME = os.getenv("APP_NAME", "DavnorShield")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.PROJECT_NAME = os.getenv("PROJECT_NAME", "DavnorShield")
        self.TIMEZONE = os.getenv("TIMEZONE", "Asia/Manila")

        # =========================
        # JWT
        # =========================
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

        # =========================
        # PostgreSQL
        # =========================
        self.DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost").strip()
        self.DATABASE_PORT = self._get_int("DATABASE_PORT", 5432)
        self.DATABASE_USER = os.getenv("DATABASE_USER", "postgres").strip()
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "postgres").strip()

        configured_url = os.getenv("DATABASE_URL", "").strip()
        self.DATABASE_URL = self._normalize_database_url(configured_url)
        if not self.DATABASE_URL:
            self.DATABASE_URL = self._build_database_url()

        # Keep the fields used by diagnostics aligned with the actual engine URL.
        parsed_database_url = urlsplit(self.DATABASE_URL)
        self.DATABASE_HOST = parsed_database_url.hostname or self.DATABASE_HOST
        self.DATABASE_PORT = parsed_database_url.port or self.DATABASE_PORT
        self.DATABASE_USER = parsed_database_url.username or self.DATABASE_USER
        self.DATABASE_NAME = parsed_database_url.path.lstrip("/") or self.DATABASE_NAME

        # =========================
        # Firebase
        # =========================
        self.FIREBASE_PROJECT_ID = os.getenv("PROJECT_ID", "")
        self.FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")
        self.FIREBASE_API_KEY = os.getenv("API_KEY", "")
        self.FIREBASE_AUTH_DOMAIN = os.getenv("AUTH_DOMAIN", "")
        self.FIREBASE_STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "")
        self.FIREBASE_MESSAGING_SENDER_ID = os.getenv("MESSAGING_SENDER_ID", "")
        self.FIREBASE_APP_ID = os.getenv("APP_ID", "")
        self.FIREBASE_MEASUREMENT_ID = os.getenv("MEASUREMENT_ID", "")

        # =========================
        # AI
        # =========================
        self.AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")
        self.AI_MODEL = os.getenv("GROQ_MODEL", "")
        self.AI_API_KEY = os.getenv(
            "AI_API_KEY",
            os.getenv("GROQ_API_KEY1", ""),
        )

        keys = os.getenv("GROQ_API_KEYS", "")
        self.GROQ_API_KEYS = tuple(k.strip() for k in keys.split(",") if k.strip())

        self.GROQ_API_KEY1 = os.getenv("GROQ_API_KEY1", "")
        self.GROQ_API_KEY2 = os.getenv("GROQ_API_KEY2", "")
        self.GROQ_API_KEY3 = os.getenv("GROQ_API_KEY3", "")
        self.GROQ_API_KEY4 = os.getenv("GROQ_API_KEY4", "")
        self.GROQ_API_KEY5 = os.getenv("GROQ_API_KEY5", "")

        self.GROQ_BASE_URL = os.getenv(
            "GROQ_BASE_URL",
            "https://api.groq.com/openai/v1",
        )

        self.GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "120"))

        self.DEFAULT_MAX_CONTEXT_TOKENS = self._get_int(
            "DEFAULT_MAX_CONTEXT_TOKENS", 6000
        )
        self.DEFAULT_MAX_HISTORY_MESSAGES = self._get_int(
            "DEFAULT_MAX_HISTORY_MESSAGES", 20
        )
        self.DEFAULT_MAX_TOOL_OUTPUT_CHARS = self._get_int(
            "DEFAULT_MAX_TOOL_OUTPUT_CHARS", 3000
        )
        self.DEFAULT_MAX_FILE_SIZE = self._get_int("DEFAULT_MAX_FILE_SIZE", 10000)
        self.DEFAULT_MAX_FILE_LIST_ITEMS = self._get_int(
            "DEFAULT_MAX_FILE_LIST_ITEMS", 50
        )
        self.DEFAULT_MAX_OUTPUT_LINES = self._get_int("DEFAULT_MAX_OUTPUT_LINES", 100)
        self.DEFAULT_RESERVE_RESPONSE_TOKENS = self._get_int(
            "DEFAULT_RESERVE_RESPONSE_TOKENS", 1000
        )
        self.THREAT_SCORE_THRESHOLD = float(
            os.getenv("THREAT_SCORE_THRESHOLD", "70.0")
        )
        self.AI_MIN_RISK_SCORE = float(os.getenv("AI_MIN_RISK_SCORE", "50.0"))
        self.AI_OUTBREAK_THRESHOLD = self._get_int("AI_OUTBREAK_THRESHOLD", 10)
        self.AI_SIMILARITY_THRESHOLD = float(
            os.getenv("AI_SIMILARITY_THRESHOLD", "60.0")
        )

        # =========================
        # Scheduler
        # =========================
        self.OUTBREAK_INTERVAL_MINUTES = int(
            os.getenv("OUTBREAK_INTERVAL_MINUTES", "10")
        )
        self.WEATHER_INTERVAL_HOURS = int(
            os.getenv("WEATHER_INTERVAL_HOURS", "24")
        )
        self.SCHEDULER_ENABLED = (
            os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
        )
        self.SCHEDULER_TIMEZONE = os.getenv(
            "SCHEDULER_TIMEZONE",
            "Asia/Manila",
        )
        self.NOTIFICATION_INTERVAL_SECONDS = self._get_int(
            "NOTIFICATION_INTERVAL_SECONDS", 60
        )
        self.CLEANUP_CRON_HOUR = self._get_int("CLEANUP_CRON_HOUR", 2)
        self.ANALYTICS_INTERVAL_SECONDS = self._get_int(
            "ANALYTICS_INTERVAL_SECONDS", 3600
        )

        # =========================
        # Uploads
        # =========================
        self.UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIRECTORY", "uploads")
        self.MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

        # =========================
        # CORS Origins
        # =========================
        origins = os.getenv(
            "ALLOWED_ORIGINS",
            '["http://localhost:3000","http://127.0.0.1:3000"]',
        )

        try:
            self.ALLOWED_ORIGINS = json.loads(origins)
        except json.JSONDecodeError:
            self.ALLOWED_ORIGINS = [o.strip() for o in origins.split(",") if o.strip()]

    @staticmethod
    def _get_int(name: str, default: int) -> int:
        """Read an integer setting while preserving a safe default."""

        try:
            return int(os.getenv(name, str(default)))
        except ValueError:
            return default

    def _build_database_url(self) -> str:
        """Build a SQLAlchemy async URL when DATABASE_URL is absent or invalid."""

        username = quote(self.DATABASE_USER, safe="")
        password = quote(self.DATABASE_PASSWORD, safe="")
        database = quote(self.DATABASE_NAME, safe="")

        return urlunsplit(
            (
                "postgresql+asyncpg",
                f"{username}:{password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}",
                f"/{database}",
                "",
                "",
            )
        )

    @staticmethod
    def _normalize_database_url(url: str) -> str:
        """Return an async PostgreSQL URL, or an empty string for invalid input."""

        if not url:
            return ""

        try:
            parsed = urlsplit(url)
            port = parsed.port or 5432
        except ValueError:
            return ""

        if parsed.scheme not in {"postgresql", "postgres", "postgresql+asyncpg"}:
            return ""

        if not parsed.hostname or not parsed.path.lstrip("/"):
            return ""

        username = quote(parsed.username or "", safe="")
        password = quote(parsed.password or "", safe="")
        host = parsed.hostname
        database = quote(parsed.path.lstrip("/"), safe="")

        return urlunsplit(
            (
                "postgresql+asyncpg",
                f"{username}:{password}@{host}:{port}",
                f"/{database}",
                parsed.query,
                "",
            )
        )

    @property
    def UPLOAD_DIR(self):
        return self.UPLOAD_DIRECTORY

    @property
    def REPORT_IMAGE_DIR(self):
        return f"{self.UPLOAD_DIRECTORY.rstrip('/')}/reports"

    @property
    def OUTBREAK_INTERVAL_SECONDS(self):
        return self.OUTBREAK_INTERVAL_MINUTES * 60


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
