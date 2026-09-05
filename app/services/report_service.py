"""Scam report business logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ReportStatus, ThreatCategory
from app.models.scam_report import ScamReport
from app.repositories.report_repository import ReportRepository
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.services.outbreak_service import OutbreakService
from app.services.pattern_service import PatternAnalysisResult, PatternService
from app.utils.file_upload import save_report_image
from app.utils.risk_calculator import calculate_risk_score


@dataclass(slots=True)
class ReportSubmissionResult:
    """Result of creating and processing a report."""

    report: ScamReport
    pattern_analysis: PatternAnalysisResult | None
    outbreak: object | None


class ReportService:
    """Business logic around scam reports."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.reports = ReportRepository(db)
        self.patterns = PatternService(db)
        self.outbreaks = OutbreakService(db)
        self.notifications = NotificationService(db)
        self.audit = AuditService(db)

    async def upload_screenshot(
        self,
        file_bytes: bytes,
        original_filename: str,
        upload_dir: str | Path = "uploads/reports",
    ) -> str:
        """Persist a screenshot and return its filesystem path."""

        return str(save_report_image(file_bytes, original_filename, upload_dir=upload_dir))

    def calculate_initial_threat_score(
        self,
        *,
        suspicious_url: str | None = None,
        phone_number: str | None = None,
        qr_data: str | None = None,
        description: str = "",
        duplicate_reports: int = 0,
        outbreak_score: float = 0.0,
    ) -> float:
        """Calculate an initial threat score for a report."""

        return calculate_risk_score(
            malicious_url=suspicious_url is not None,
            suspicious_keywords=len(description.split()),
            duplicate_reports=duplicate_reports,
            outbreak_score=outbreak_score,
            suspicious_phone=phone_number is not None,
            qr_match=qr_data is not None,
        )

    async def verify_duplicate_reports(
        self,
        *,
        municipality_id: UUID,
        barangay_id: UUID,
        suspicious_url: str | None = None,
        phone_number: str | None = None,
        qr_data: str | None = None,
        limit: int = 50,
    ) -> list[ScamReport]:
        """Find likely duplicate reports in the same locality."""

        recent_reports = await self.reports.get_recent_reports(
            limit=limit,
            municipality_id=municipality_id,
            barangay_id=barangay_id,
        )
        duplicates: list[ScamReport] = []
        for report in recent_reports:
            if suspicious_url and report.suspicious_url == suspicious_url:
                duplicates.append(report)
                continue
            if phone_number and report.phone_number == phone_number:
                duplicates.append(report)
                continue
            if qr_data and report.qr_data == qr_data:
                duplicates.append(report)
        return duplicates

    async def submit_scam_report(
        self,
        *,
        user_id: UUID,
        municipality_id: UUID,
        barangay_id: UUID,
        report_type: str,
        title: str,
        description: str,
        suspicious_url: str | None = None,
        phone_number: str | None = None,
        qr_data: str | None = None,
        screenshot_bytes: bytes | None = None,
        screenshot_filename: str | None = None,
    ) -> ReportSubmissionResult:
        """Create a report and run pattern/outbreak workflows."""

        duplicates = await self.verify_duplicate_reports(
            municipality_id=municipality_id,
            barangay_id=barangay_id,
            suspicious_url=suspicious_url,
            phone_number=phone_number,
            qr_data=qr_data,
        )
        initial_score = self.calculate_initial_threat_score(
            suspicious_url=suspicious_url,
            phone_number=phone_number,
            qr_data=qr_data,
            description=description,
            duplicate_reports=len(duplicates),
        )
        screenshot_path = None
        if screenshot_bytes is not None and screenshot_filename is not None:
            screenshot_path = await self.upload_screenshot(
                screenshot_bytes,
                screenshot_filename,
            )

        report = await self.reports.create_report(
            {
                "user_id": user_id,
                "municipality_id": municipality_id,
                "barangay_id": barangay_id,
                "report_type": report_type,
                "title": title,
                "description": description,
                "suspicious_url": suspicious_url,
                "phone_number": phone_number,
                "qr_data": qr_data,
                "screenshot_path": screenshot_path,
                "threat_score": initial_score,
                "threat_category": self._infer_category(
                    report_type,
                    suspicious_url,
                    phone_number,
                    qr_data,
                ),
                "status": ReportStatus.pending,
            }
        )
        pattern_analysis = await self.patterns.analyze_report_patterns(report)
        outbreak = None
        if report.barangay_id is not None:
            outbreak = await self.outbreaks.calculate_barangay_outbreak(report.barangay_id)
        if outbreak is not None and getattr(outbreak, "detected", False):
            await self.notifications.broadcast_outbreak(
                title="Outbreak Alert",
                message=getattr(outbreak, "message", "A report outbreak has been detected."),
                municipality_id=report.municipality_id,
                barangay_id=report.barangay_id,
                data={"report_id": str(report.id)},
            )
        await self.audit.log_report_submission(
            user_id=user_id,
            endpoint="/reports",
            report_id=report.id,
        )
        return ReportSubmissionResult(
            report=report,
            pattern_analysis=pattern_analysis,
            outbreak=outbreak,
        )

    async def update_report_status(self, report_id: UUID, status_value: ReportStatus) -> ScamReport:
        """Update a report status."""

        updated = await self.reports.update_report_status(report_id, status_value)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        return updated

    async def get_report(self, report_id: UUID) -> ScamReport:
        """Return a report by UUID."""

        report = await self.reports.get_report(report_id)
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        return report

    async def delete_report(self, report_id: UUID) -> bool:
        """Delete a report."""

        deleted = await self.reports.delete_report(report_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        return deleted

    async def get_reports_feed(
        self,
        *,
        page: int = 1,
        size: int = 20,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        threat_category: ThreatCategory | None = None,
        status_filter: ReportStatus | None = None,
    ) -> tuple[list[ScamReport], int]:
        """Return a report feed for dashboards."""

        return await self.reports.list_reports(
            page=page,
            size=size,
            municipality_id=municipality_id,
            barangay_id=barangay_id,
            threat_category=threat_category,
            status=status_filter,
        )

    async def list_reports(
        self,
        *,
        page: int = 1,
        size: int = 20,
        threat_category: ThreatCategory | None = None,
        status: ReportStatus | None = None,
        municipality_id: UUID | None = None,
        barangay_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[ScamReport], int]:
        """Return reports with full filtering support."""

        return await self.reports.list_reports(
            page=page,
            size=size,
            threat_category=threat_category,
            status=status,
            municipality_id=municipality_id,
            barangay_id=barangay_id,
            start_date=start_date,
            end_date=end_date,
        )

    def _infer_category(
        self,
        report_type: str,
        suspicious_url: str | None,
        phone_number: str | None,
        qr_data: str | None,
    ) -> ThreatCategory:
        """Infer a report category from submitted signals."""

        normalized = report_type.lower()
        if suspicious_url:
            return ThreatCategory.phishing
        if qr_data:
            return ThreatCategory.qr_scam
        if phone_number:
            return ThreatCategory.sms_scam
        if "market" in normalized or "seller" in normalized:
            return ThreatCategory.marketplace_scam
        return ThreatCategory.other
