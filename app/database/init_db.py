from __future__ import annotations
import asyncio
import logging
import socket
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import asyncpg
from sqlalchemy.exc import DBAPIError, OperationalError

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.database.base import Base
from app.database.session import engine
from app.config import settings

from app.models import alert as _alert 
from app.models import audit_log as _audit_log  
from app.models import barangay as _barangay  
from app.models import cyber_weather as _cyber_weather  
from app.models import municipality as _municipality  
from app.models import notification as _notification  
from app.models import scam_report as _scam_report 
from app.models import school as _school  
from app.models import threat_pattern as _threat_pattern  
from app.models import user as _user  
from app.models import chat as _chat  


logger = logging.getLogger(__name__)


class DatabaseInitializationError(RuntimeError):
    """Raised when application startup cannot reach the configured database."""


def _mask_database_url(database_url: str) -> str:

    parsed = urlsplit(database_url)
    username = parsed.username or ""
    password = ":***" if parsed.password is not None else ""
    credentials = f"{username}{password}@" if username else ""
    host = parsed.hostname or "<missing-host>"
    port = f":{parsed.port}" if parsed.port else ""
    return urlunsplit(
        (parsed.scheme, f"{credentials}{host}{port}", parsed.path, parsed.query, "")
    )

def _find_exception(error: BaseException, exception_type: type[BaseException]) -> bool:
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        if isinstance(current, exception_type):
            return True
        seen.add(id(current))
        current = getattr(current, "orig", None) or current.__cause__ or current.__context__
    return False


def _print_database_diagnostics() -> bool:
    logger.info(
        "Connecting to PostgreSQL host=%s port=%s database=%s",
        settings.DATABASE_HOST,
        settings.DATABASE_PORT,
        settings.DATABASE_NAME,
    )
    print(f"Database URL: {_mask_database_url(settings.DATABASE_URL)}")
    print(f"Database host: {settings.DATABASE_HOST}")
    print(f"Database port: {settings.DATABASE_PORT}")
    print(f"Database name: {settings.DATABASE_NAME}")
    try:
        socket.getaddrinfo(settings.DATABASE_HOST, settings.DATABASE_PORT)
    except socket.gaierror as error:
        message = (
            f"Database DNS resolution failed for '{settings.DATABASE_HOST}': {error}. "
            "Use Render's full external hostname from its Connect menu, not its "
            "short internal hostname (for example, *.oregon-postgres.render.com)."
        )
        logger.error(message)
        print(message, file=sys.stderr)
        return False

    print("Database DNS resolution: succeeded")
    return True


async def init_database() -> None:
    if not _print_database_diagnostics():
        await engine.dispose()
        raise DatabaseInitializationError("Database is unreachable because its hostname cannot be resolved.")

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    except (
        OperationalError,
        DBAPIError,
        OSError,
        asyncpg.InvalidCatalogNameError,
        asyncpg.PostgresConnectionError,
    ) as error:
        await engine.dispose()
        if _find_exception(error, socket.gaierror):
            message = (
                f"Database DNS resolution failed for '{settings.DATABASE_HOST}'. "
                "Set DATABASE_URL and DATABASE_HOST to Render's full external FQDN."
            )
        elif _find_exception(error, asyncpg.InvalidCatalogNameError):
            message = (
                f"Database '{settings.DATABASE_NAME}' does not exist on "
                f"'{settings.DATABASE_HOST}'. Verify DATABASE_NAME."
            )
        else:
            message = (
                f"Could not connect to PostgreSQL at {settings.DATABASE_HOST}:"
                f"{settings.DATABASE_PORT}. Verify credentials, network access, "
                "and the Render external connection URL."
            )
        logger.error("%s Original error: %s", message, error)
        raise DatabaseInitializationError(message) from error


async def main() -> None:
    """Run the database initialization routine."""

    await init_database()
    print("Database schema initialized.")


if __name__ == "__main__":
    asyncio.run(main())