"""Data cleanup worker."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from app.config import settings
from app.database.session import AsyncSessionLocal
from app.models.enums import ReportStatus
from app.services.alert_service import AlertService
from app.services.report_service import ReportService
from app.utils.date_utils import utc_now
from app.utils.file_upload import delete_image


async def run_cleanup_job() -> dict[str, object]:
    """Delete expired alerts, orphan screenshots, and archived reports."""

    async with AsyncSessionLocal() as db:
        alert_service = AlertService(db)
        report_service = ReportService(db)
        archived_reports, _ = await report_service.get_reports_feed(
            page=1,
            size=1000,
            status_filter=ReportStatus.resolved,
        )
        removed_reports = 0
        screenshot_paths: set[str] = set()
        for report in archived_reports:
            if report.reported_at < utc_now() - timedelta(days=90):
                if report.screenshot_path:
                    screenshot_paths.add(report.screenshot_path)
                await report_service.delete_report(report.id)
                removed_reports += 1

        current_reports, _ = await report_service.get_reports_feed(page=1, size=5000)
        referenced_paths = {report.screenshot_path for report in current_reports if report.screenshot_path}
        for path in screenshot_paths:
            if path not in referenced_paths:
                delete_image(path)

        alerts, _ = await alert_service.list_alerts(page=1, size=5000, is_active=False)
        removed_alerts = 0
        for alert in alerts:
            if alert.created_at < utc_now() - timedelta(days=30):
                await alert_service.delete_alert(alert.id)
                removed_alerts += 1

        return {
            "archived_reports_deleted": removed_reports,
            "expired_alerts_deleted": removed_alerts,
        }
