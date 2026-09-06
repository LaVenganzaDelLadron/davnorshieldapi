from __future__ import annotations
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.barangay_repository import BarangayRepository
from app.repositories.municipality_repository import MunicipalityRepository
from app.repositories.report_repository import ReportRepository
from app.services.heatmap_service import HeatmapService
from app.services.outbreak_service import OutbreakService


class DashboardService:
    """Generate dashboard aggregates for LGU users."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.reports = ReportRepository(db)
        self.barangays = BarangayRepository(db)
        self.municipalities = MunicipalityRepository(db)
        self.heatmap = HeatmapService(db)
        self.outbreaks = OutbreakService(db)

    async def _top_threat_categories(self) -> list[dict[str, object]]:
        reports, _ = await self.reports.list_reports(page=1, size=10000)
        counter: Counter[str] = Counter(report.threat_category.value for report in reports)
        return [
            {"category": category, "count": count}
            for category, count in counter.most_common(5)
        ]

    async def _ranking_by_municipality(self) -> list[dict[str, object]]:
        municipalities = await self.municipalities.list_municipalities()
        ranking: list[dict[str, object]] = []
        for municipality in municipalities:
            count = await self.reports.count_reports_by_municipality(municipality.id)
            ranking.append(
                {
                    "id": str(municipality.id),
                    "name": municipality.municipality_name,
                    "report_count": count,
                }
            )
        return sorted(ranking, key=lambda item: item["report_count"], reverse=True)

    async def _ranking_by_barangay(self) -> list[dict[str, object]]:
        barangays = await self.barangays.list_barangays()
        ranking: list[dict[str, object]] = []
        for barangay in barangays:
            count = await self.reports.count_reports_by_barangay(barangay.id)
            ranking.append(
                {
                    "id": str(barangay.id),
                    "name": barangay.barangay_name,
                    "municipality_id": str(barangay.municipality_id),
                    "report_count": count,
                }
            )
        return sorted(ranking, key=lambda item: item["report_count"], reverse=True)

    async def _active_outbreaks(self) -> list[dict[str, object]]:
        municipalities = await self.municipalities.list_municipalities()
        outbreaks: list[dict[str, object]] = []
        for municipality in municipalities:
            metadata = await self.outbreaks.calculate_municipality_outbreak(municipality.id)
            if metadata.detected:
                outbreaks.append(
                    {
                        "scope": metadata.scope,
                        "scope_id": str(metadata.scope_id),
                        "count": metadata.count,
                        "severity": metadata.severity,
                    }
                )
        return outbreaks

    async def generate_dashboard(self) -> dict[str, object]:
        """Return a consolidated LGU dashboard payload."""

        reports, total_reports = await self.reports.list_reports(page=1, size=10000)
        return {
            "total_reports": total_reports,
            "active_outbreaks": await self._active_outbreaks(),
            "heatmap_statistics": await self.heatmap.generate_heatmap(),
            "top_threat_categories": await self._top_threat_categories(),
            "municipality_ranking": await self._ranking_by_municipality(),
            "barangay_ranking": await self._ranking_by_barangay(),
            "recent_reports": [
                {
                    "id": str(report.id),
                    "title": report.title,
                    "threat_category": report.threat_category.value,
                    "status": report.status.value,
                }
                for report in reports[:10]
            ],
        }

