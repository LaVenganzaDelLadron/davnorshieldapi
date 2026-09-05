"""Outbreak detection over a sliding 24-hour window."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import UUID


@dataclass(slots=True)
class OutbreakResult:
    """Structured outbreak metadata."""

    detected: bool
    threshold: int
    window_hours: int
    total_reports: int
    barangay_groups: dict[str, int] = field(default_factory=dict)
    municipality_groups: dict[str, int] = field(default_factory=dict)
    category_groups: dict[str, int] = field(default_factory=dict)


def detect_outbreak(
    reports: Iterable[dict[str, object]],
    *,
    threshold: int = 10,
    window_hours: int = 24,
    reference_time: datetime | None = None,
) -> OutbreakResult:
    """Detect outbreaks from report payloads without touching persistence."""

    now = reference_time or datetime.now(tz=timezone.utc)
    start = now - timedelta(hours=window_hours)
    filtered: list[dict[str, object]] = []
    for report in reports:
        reported_at = report.get("reported_at")
        if isinstance(reported_at, datetime):
            if reported_at.tzinfo is None:
                reported_at = reported_at.replace(tzinfo=timezone.utc)
            if start <= reported_at <= now:
                filtered.append(report)

    barangay_groups = Counter(str(report.get("barangay_name") or report.get("barangay_id") or "unknown") for report in filtered)
    municipality_groups = Counter(str(report.get("municipality_name") or report.get("municipality_id") or "unknown") for report in filtered)
    category_groups = Counter(str(report.get("threat_category") or "other") for report in filtered)

    total_reports = len(filtered)
    detected = total_reports >= threshold
    return OutbreakResult(
        detected=detected,
        threshold=threshold,
        window_hours=window_hours,
        total_reports=total_reports,
        barangay_groups=dict(barangay_groups),
        municipality_groups=dict(municipality_groups),
        category_groups=dict(category_groups),
    )

