from __future__ import annotations
from collections.abc import Mapping
from uuid import UUID
from sqlalchemy import select
from app.models.alert import Alert
from app.repositories.base import RepositoryBase



class AlertRepository(RepositoryBase):
    """Database operations for alerts."""

    async def create_alert(self, alert_data: Mapping[str, object]) -> Alert:
        """Create an alert."""

        alert = Alert(**self._mapping_data(alert_data))
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_alert(self, alert_id: UUID) -> Alert | None:
        """Fetch an alert by UUID."""

        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    async def deactivate_alert(self, alert_id: UUID) -> Alert | None:
        """Set an alert as inactive."""

        alert = await self.get_alert(alert_id)
        if alert is None:
            return None
        alert.is_active = False
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def delete_alert(self, alert_id: UUID) -> bool:
        """Delete an alert by UUID."""

        alert = await self.get_alert(alert_id)
        if alert is None:
            return False
        await self.db.delete(alert)
        await self.db.commit()
        return True

    async def list_alerts(
        self,
        *,
        page: int = 1,
        size: int = 20,
        is_active: bool | None = None,
    ) -> tuple[list[Alert], int]:
        """List alerts with pagination."""

        stmt = select(Alert)
        count_stmt = self._count_statement(Alert)
        if is_active is not None:
            stmt = stmt.where(Alert.is_active.is_(is_active))
            count_stmt = count_stmt.where(Alert.is_active.is_(is_active))
        stmt = stmt.order_by(Alert.created_at.desc())
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_active_alerts(
        self,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Alert], int]:
        """List only active alerts."""

        return await self.list_alerts(page=page, size=size, is_active=True)

    async def list_barangay_alerts(
        self,
        barangay_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Alert], int]:
        """List alerts for a barangay."""

        stmt = select(Alert).where(Alert.barangay_id == barangay_id).order_by(Alert.created_at.desc())
        count_stmt = self._count_statement(Alert, Alert.barangay_id == barangay_id)
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_municipality_alerts(
        self,
        municipality_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Alert], int]:
        """List alerts for a municipality."""

        stmt = (
            select(Alert)
            .where(Alert.municipality_id == municipality_id)
            .order_by(Alert.created_at.desc())
        )
        count_stmt = self._count_statement(Alert, Alert.municipality_id == municipality_id)
        return await self._paginate(stmt, count_stmt, page=page, size=size)











