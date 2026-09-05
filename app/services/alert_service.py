"""Alert management service."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.enums import AlertLevel
from app.repositories.alert_repository import AlertRepository
from app.services.notification_service import NotificationService
from app.utils.date_utils import today_date, utc_now


class AlertService:
    """Business logic for alert creation, listing, and broadcasting."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.alerts = AlertRepository(db)
        self.notifications = NotificationService(db)

    async def get_alert(self, alert_id: UUID) -> Alert | None:
        """Return an alert by UUID."""

        return await self.alerts.get_alert(alert_id)

    async def list_alerts(
        self,
        *,
        page: int = 1,
        size: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[Alert], int]:
        """Return alerts with pagination."""

        return await self.alerts.list_alerts(page=page, size=size, is_active=is_active)

    async def list_today_alerts(self) -> tuple[list[Alert], int]:
        """Return alerts created today."""

        alerts, total = await self.list_alerts(page=1, size=1000, is_active=None)
        start = datetime.combine(today_date(), time.min).replace(tzinfo=utc_now().tzinfo)
        end = datetime.combine(today_date(), time.max).replace(tzinfo=utc_now().tzinfo)
        filtered = [alert for alert in alerts if start <= alert.created_at <= end]
        return filtered, len(filtered)

    async def list_barangay_alerts(
        self,
        barangay_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Alert], int]:
        """Return alerts for a barangay."""

        return await self.alerts.list_barangay_alerts(barangay_id, page=page, size=size)

    async def list_municipality_alerts(
        self,
        municipality_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Alert], int]:
        """Return alerts for a municipality."""

        return await self.alerts.list_municipality_alerts(municipality_id, page=page, size=size)

    async def create_alert(self, payload: dict[str, object]) -> Alert:
        """Create an alert record."""

        return await self.alerts.create_alert(payload)

    async def deactivate_alert(self, alert_id: UUID) -> Alert:
        """Deactivate an alert or raise 404."""

        alert = await self.alerts.deactivate_alert(alert_id)
        if alert is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
        return alert

    async def delete_alert(self, alert_id: UUID) -> bool:
        """Delete an alert or raise 404."""

        deleted = await self.alerts.delete_alert(alert_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
        return deleted

    async def broadcast_alert(
        self,
        *,
        threat_pattern_id: UUID,
        municipality_id: UUID,
        barangay_id: UUID | None,
        alert_level: object,
        title: str,
        message: str,
    ) -> Alert:
        """Create an alert and notify the intended scope."""

        normalized_level = self._normalize_alert_level(alert_level)
        alert = await self.create_alert(
            {
                "threat_pattern_id": threat_pattern_id,
                "municipality_id": municipality_id,
                "barangay_id": barangay_id,
                "alert_level": normalized_level,
                "title": title,
                "message": message,
                "is_active": True,
            }
        )
        if barangay_id is not None:
            await self.notifications.notify_barangay(barangay_id, title, message, data={"alert_id": str(alert.id)})
        else:
            await self.notifications.notify_municipality(
                municipality_id,
                title,
                message,
                data={"alert_id": str(alert.id)},
            )
        return alert

    def _normalize_alert_level(self, alert_level: object) -> AlertLevel:
        """Normalize any alert level representation to the model enum."""

        if isinstance(alert_level, AlertLevel):
            return alert_level
        value = str(alert_level).strip().lower()
        if value == "low":
            return AlertLevel.low
        if value == "medium":
            return AlertLevel.medium
        if value == "high":
            return AlertLevel.high
        return AlertLevel.critical
