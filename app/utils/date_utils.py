from __future__ import annotations
from datetime import UTC, date, datetime, timedelta


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def today_date() -> date:
    return utc_now().date()


def format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()


def within_last_24_hours(value: datetime, reference: datetime | None = None) -> bool:
    now = reference or utc_now()
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return now - timedelta(hours=24) <= value.astimezone(UTC) <= now

