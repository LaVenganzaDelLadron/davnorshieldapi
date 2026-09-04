"""Date and timestamp helpers."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""

    return datetime.now(tz=UTC)


def today_date() -> date:
    """Return today's date in UTC."""

    return utc_now().date()


def format_timestamp(value: datetime) -> str:
    """Format a timestamp using an ISO 8601 representation."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()


def within_last_24_hours(value: datetime, reference: datetime | None = None) -> bool:
    """Return True when a timestamp falls within the last 24 hours."""

    now = reference or utc_now()
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return now - timedelta(hours=24) <= value.astimezone(UTC) <= now

