"""Audit logging service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_repository import AuditRepository
from app.utils.date_utils import utc_now


class AuditService:
    """Create structured audit logs for sensitive actions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.audit = AuditRepository(db)

    async def log_action(
        self,
        *,
        action: str,
        endpoint: str,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a generic action."""

        await self.audit.create_log(
            {
                "user_id": user_id,
                "action": action,
                "endpoint": endpoint,
                "ip_address": ip_address,
                "device": device,
                "created_at": utc_now(),
            }
        )

    async def log_login(
        self,
        *,
        user_id: UUID | None,
        endpoint: str = "/auth/login",
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a login event."""

        await self.log_action(
            action="login",
            endpoint=endpoint,
            user_id=user_id,
            ip_address=ip_address,
            device=device,
        )

    async def log_report_submission(
        self,
        *,
        user_id: UUID,
        endpoint: str,
        report_id: UUID,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log a report submission."""

        await self.log_action(
            action=f"report_submission:{report_id}",
            endpoint=endpoint,
            user_id=user_id,
            ip_address=ip_address,
            device=device,
        )

    async def log_admin_action(
        self,
        *,
        user_id: UUID,
        action: str,
        endpoint: str,
        ip_address: str | None = None,
        device: str | None = None,
    ) -> None:
        """Log an administrative action."""

        await self.log_action(
            action=f"admin:{action}",
            endpoint=endpoint,
            user_id=user_id,
            ip_address=ip_address,
            device=device,
        )

