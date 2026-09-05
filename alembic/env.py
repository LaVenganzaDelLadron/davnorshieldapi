"""Alembic environment for async PostgreSQL migrations."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.database.base import Base
from app.config import settings

# Import all models so metadata is populated.
from app.models import alert as _alert  # noqa: F401
from app.models import audit_log as _audit_log  # noqa: F401
from app.models import barangay as _barangay  # noqa: F401
from app.models import cyber_weather as _cyber_weather  # noqa: F401
from app.models import municipality as _municipality  # noqa: F401
from app.models import notification as _notification  # noqa: F401
from app.models import scam_report as _scam_report  # noqa: F401
from app.models import school as _school  # noqa: F401
from app.models import threat_pattern as _threat_pattern  # noqa: F401
from app.models import user as _user  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Return the migration database URL from centralized settings."""

    database_url = settings.DATABASE_URL or config.get_main_option("sqlalchemy.url")
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations against a live connection."""

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations using an async engine."""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
