from __future__ import annotations
from collections.abc import Mapping
from datetime import UTC, date, datetime, time, timedelta
from uuid import UUID
from sqlalchemy import and_, func, or_, select
from app.models.enums import ReportStatus, ThreatCategory
from app.models.scam_report import ScamReport
from app.repositories.base import RepositoryBase
from app.utils.date_utils import utc_now


def _to_aware_datetime(value: date | datetime | None, *, end_of_day: bool = False) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    return datetime.combine(value, time.max if end_of_day else time.min, tzinfo=UTC)


class ReportRepository(RepositoryBase):
    """Database operations for scam reports."""

    async def create_report(self, report_data: Mapping[str, object]) -> ScamReport:
        """Create and persist a scam report."""

        report = ScamReport(**self._mapping_data(report_data))
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report(self, report_id: UUID) -> ScamReport | None:
        """Fetch a scam report by UUID."""

        result = await self.db.execute(select(ScamReport).where(ScamReport.id == report_id))
        return result.scalar_one_or_none()

    async def update_report_status(self, report_id: UUID, status: ReportStatus) -> ScamReport | None:
        """Update the report status."""

        report = await self.get_report(report_id)
        if report is None:
            return None
        report.status = status
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def delete_report(self, report_id: UUID) -> bool:
        """Delete a report by UUID."""

        report = await self.get_report(report_id)
        if report is None:
            return False
        await self.db.delete(report)
        await self.db.commit()
        return True

    async def list_reports(
        self,
        *,
        page: int = 1,
        size: int = 20,
        threat_category: ThreatCategory | None = None,
        status: ReportStatus | None = None,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> tuple[list[ScamReport], int]:
        """List reports with filters and pagination."""

        stmt = select(ScamReport)
        count_stmt = self._count_statement(ScamReport)
        filters = []
        if threat_category is not None:
            filters.append(ScamReport.threat_category == threat_category)
        if status is not None:
            filters.append(ScamReport.status == status)
        if municipality_id is not None:
            filters.append(ScamReport.municipality_id == municipality_id)
        if barangay_id is not None:
            filters.append(ScamReport.barangay_id == barangay_id)
        start_dt = _to_aware_datetime(start_date)
        end_dt = _to_aware_datetime(end_date, end_of_day=True)
        if start_dt is not None:
            filters.append(ScamReport.reported_at >= start_dt)
        if end_dt is not None:
            filters.append(ScamReport.reported_at <= end_dt)
        if filters:
            stmt = stmt.where(and_(*filters))
            count_stmt = count_stmt.where(and_(*filters))
        stmt = stmt.order_by(ScamReport.reported_at.desc())
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_reports_by_barangay(
        self,
        barangay_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[ScamReport], int]:
        """List reports for a barangay."""

        return await self.list_reports(page=page, size=size, barangay_id=barangay_id)

    async def list_reports_by_municipality(
        self,
        municipality_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[ScamReport], int]:
        """List reports for a municipality."""

        return await self.list_reports(page=page, size=size, municipality_id=municipality_id)

    async def get_reports_by_category(
        self,
        category: ThreatCategory,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[ScamReport], int]:
        """Return reports for a specific threat category."""

        return await self.list_reports(page=page, size=size, threat_category=category)

    async def get_recent_reports(
        self,
        *,
        limit: int = 10,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        hours: int = 24,
    ) -> list[ScamReport]:
        """Return the most recent reports within a time window."""

        since = utc_now() - timedelta(hours=hours)
        stmt = select(ScamReport).where(ScamReport.reported_at >= since)
        if municipality_id is not None:
            stmt = stmt.where(ScamReport.municipality_id == municipality_id)
        if barangay_id is not None:
            stmt = stmt.where(ScamReport.barangay_id == barangay_id)
        stmt = stmt.order_by(ScamReport.reported_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_reports_by_barangay(
        self,
        barangay_id: UUID,
        *,
        threat_category: ThreatCategory | None = None,
        status: ReportStatus | None = None,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> int:
        """Count reports for a barangay."""

        return await self._count_reports(
            barangay_id=barangay_id,
            threat_category=threat_category,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

    async def count_reports_by_municipality(
        self,
        municipality_id: UUID,
        *,
        threat_category: ThreatCategory | None = None,
        status: ReportStatus | None = None,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> int:
        """Count reports for a municipality."""

        return await self._count_reports(
            municipality_id=municipality_id,
            threat_category=threat_category,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

    async def _count_reports(
        self,
        *,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        threat_category: ThreatCategory | None = None,
        status: ReportStatus | None = None,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(ScamReport)
        filters = []
        if municipality_id is not None:
            filters.append(ScamReport.municipality_id == municipality_id)
        if barangay_id is not None:
            filters.append(ScamReport.barangay_id == barangay_id)
        if threat_category is not None:
            filters.append(ScamReport.threat_category == threat_category)
        if status is not None:
            filters.append(ScamReport.status == status)
        start_dt = _to_aware_datetime(start_date)
        end_dt = _to_aware_datetime(end_date, end_of_day=True)
        if start_dt is not None:
            filters.append(ScamReport.reported_at >= start_dt)
        if end_dt is not None:
            filters.append(ScamReport.reported_at <= end_dt)
        if filters:
            stmt = stmt.where(and_(*filters))
        return int(await self.db.scalar(stmt) or 0)

