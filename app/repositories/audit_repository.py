"""Audit log repository."""

from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.repositories.base import RepositoryBase


class AuditRepository(RepositoryBase):
    """Database operations for audit logs."""

    async def create_log(self, log_data: Mapping[str, object]) -> AuditLog:
        """Create a new audit log record."""

        log = AuditLog(**self._mapping_data(log_data))
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def list_logs(
        self,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List all audit logs."""

        stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
        count_stmt = self._count_statement(AuditLog)
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_logs_by_user(
        self,
        user_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs for a specific user."""

        stmt = select(AuditLog).where(AuditLog.user_id == user_id).order_by(AuditLog.created_at.desc())
        count_stmt = self._count_statement(AuditLog, AuditLog.user_id == user_id)
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_logs_by_endpoint(
        self,
        endpoint: str,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs for an endpoint."""

        stmt = select(AuditLog).where(AuditLog.endpoint == endpoint).order_by(AuditLog.created_at.desc())
        count_stmt = self._count_statement(AuditLog, AuditLog.endpoint == endpoint)
        return await self._paginate(stmt, count_stmt, page=page, size=size)

