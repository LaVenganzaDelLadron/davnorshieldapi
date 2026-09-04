"""Outbreak detection service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.report_repository import ReportRepository
from app.utils.constants import DEFAULT_OUTBREAK_THRESHOLD, OUTBREAK_WINDOW_HOURS
from app.utils.date_utils import utc_now


@dataclass(slots=True)
class OutbreakMetadata:
    """Structured outbreak detection output."""

    detected: bool
    count: int
    threshold: int
    window_hours: int
    scope: str
    scope_id: UUID
    severity: str
    message: str


class OutbreakService:
    """Detect report spikes over a rolling 24-hour window."""

    def __init__(self, db: AsyncSession, threshold: int = DEFAULT_OUTBREAK_THRESHOLD) -> None:
        self.db = db
        self.reports = ReportRepository(db)
        self.threshold = threshold

    def _severity(self, count: int) -> str:
        if count >= self.threshold * 3:
            return "critical"
        if count >= self.threshold * 2:
            return "high"
        if count >= self.threshold:
            return "medium"
        return "low"

    async def detect_outbreak(
        self,
        *,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        threshold: int | None = None,
    ) -> OutbreakMetadata:
        """Detect whether a scope has an outbreak in the last 24 hours."""

        active_threshold = threshold or self.threshold
        if municipality_id is None and barangay_id is None:
            raise ValueError("Either municipality_id or barangay_id must be provided.")

        if barangay_id is not None:
            count = await self.reports.count_reports_by_barangay(
                barangay_id,
                start_date=utc_now() - timedelta(hours=OUTBREAK_WINDOW_HOURS),
                end_date=utc_now(),
            )
            scope = "barangay"
            scope_id = barangay_id
        else:
            assert municipality_id is not None
            count = await self.reports.count_reports_by_municipality(
                municipality_id,
                start_date=utc_now() - timedelta(hours=OUTBREAK_WINDOW_HOURS),
                end_date=utc_now(),
            )
            scope = "municipality"
            scope_id = municipality_id

        severity = self._severity(count)
        detected = count >= active_threshold
        message = (
            f"{scope.title()} outbreak detected with {count} reports in the last "
            f"{OUTBREAK_WINDOW_HOURS} hours."
            if detected
            else f"No outbreak detected for this {scope}."
        )
        return OutbreakMetadata(
            detected=detected,
            count=count,
            threshold=active_threshold,
            window_hours=OUTBREAK_WINDOW_HOURS,
            scope=scope,
            scope_id=scope_id,
            severity=severity,
            message=message,
        )

    async def calculate_barangay_outbreak(self, barangay_id: UUID) -> OutbreakMetadata:
        """Calculate outbreak metadata for a barangay."""

        return await self.detect_outbreak(barangay_id=barangay_id)

    async def calculate_municipality_outbreak(self, municipality_id: UUID) -> OutbreakMetadata:
        """Calculate outbreak metadata for a municipality."""

        return await self.detect_outbreak(municipality_id=municipality_id)

