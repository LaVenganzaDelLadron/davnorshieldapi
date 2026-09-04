"""Barangay repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select

from app.models.barangay import Barangay
from app.repositories.base import RepositoryBase


class BarangayRepository(RepositoryBase):
    """Database operations for barangays."""

    async def get_barangay(self, barangay_id: UUID) -> Barangay | None:
        """Fetch a barangay by UUID."""

        result = await self.db.execute(select(Barangay).where(Barangay.id == barangay_id))
        return result.scalar_one_or_none()

    async def list_barangays(self) -> list[Barangay]:
        """Return all barangays ordered by name."""

        result = await self.db.execute(select(Barangay).order_by(Barangay.barangay_name))
        return list(result.scalars().all())

    async def list_barangays_by_municipality(self, municipality_id: UUID) -> list[Barangay]:
        """Return barangays within a municipality."""

        result = await self.db.execute(
            select(Barangay)
            .where(Barangay.municipality_id == municipality_id)
            .order_by(Barangay.barangay_name)
        )
        return list(result.scalars().all())

