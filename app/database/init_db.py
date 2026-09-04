"""Create all database tables for the application."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.database.base import Base
from app.database.session import engine

# Import every model module so SQLAlchemy registers the mappings.
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


async def init_database() -> None:
    """Create the full schema in the configured PostgreSQL database."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def main() -> None:
    """Run the database initialization routine."""

    await init_database()
    print("Database schema initialized.")


if __name__ == "__main__":
    asyncio.run(main())

