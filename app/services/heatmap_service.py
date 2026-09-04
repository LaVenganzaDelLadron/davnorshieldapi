"""Heatmap aggregation service."""

from __future__ import annotations

from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.barangay_repository import BarangayRepository
from app.repositories.municipality_repository import MunicipalityRepository
from app.repositories.report_repository import ReportRepository
from app.utils.geo import normalize_barangay_name, normalize_municipality_name


class HeatmapService:
    """Generate map-ready aggregates for frontend dashboards."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.reports = ReportRepository(db)
        self.barangays = BarangayRepository(db)
        self.municipalities = MunicipalityRepository(db)

    async def municipality_statistics(self) -> list[dict[str, object]]:
        """Return municipality-level report counts and density signals."""

        municipalities = await self.municipalities.list_municipalities()
        stats: list[dict[str, object]] = []
        for municipality in municipalities:
            count = await self.reports.count_reports_by_municipality(municipality.id)
            stats.append(
                {
                    "id": str(municipality.id),
                    "name": municipality.municipality_name,
                    "normalized_name": normalize_municipality_name(municipality.municipality_name),
                    "report_count": count,
                    "risk_intensity": min(count * 10, 100),
                }
            )
        return stats

    async def barangay_statistics(self) -> list[dict[str, object]]:
        """Return barangay-level report counts and density signals."""

        barangays = await self.barangays.list_barangays()
        stats: list[dict[str, object]] = []
        for barangay in barangays:
            count = await self.reports.count_reports_by_barangay(barangay.id)
            stats.append(
                {
                    "id": str(barangay.id),
                    "name": barangay.barangay_name,
                    "normalized_name": normalize_barangay_name(barangay.barangay_name),
                    "municipality_id": str(barangay.municipality_id),
                    "report_count": count,
                    "risk_intensity": min(count * 10, 100),
                }
            )
        return stats

    async def category_statistics(self) -> list[dict[str, object]]:
        """Return report counts by threat category."""

        reports, _ = await self.reports.list_reports(page=1, size=10000)
        counter: Counter[str] = Counter(report.threat_category.value for report in reports)
        return [
            {"category": category, "count": count}
            for category, count in counter.most_common()
        ]

    async def generate_heatmap(self) -> dict[str, object]:
        """Return a JSON-ready heatmap payload."""

        municipalities = await self.municipality_statistics()
        barangays = await self.barangay_statistics()
        categories = await self.category_statistics()
        return {
            "municipalities": municipalities,
            "barangays": barangays,
            "categories": categories,
        }

