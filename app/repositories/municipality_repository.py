from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from app.models.municipality import Municipality
from app.repositories.base import RepositoryBase


class MunicipalityRepository(RepositoryBase):
    """Database operations for municipalities."""

    async def get_municipality(
        self, municipality_id: UUID, *, include_inactive: bool = False
    ) -> Municipality | None:
        """Fetch a municipality by UUID."""

        stmt = select(Municipality).where(Municipality.id == municipality_id)
        if not include_inactive:
            stmt = stmt.where(Municipality.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_municipalities(self) -> list[Municipality]:
        """Return all municipalities ordered by name."""

        result = await self.db.execute(
            select(Municipality)
            .where(Municipality.is_active.is_(True))
            .order_by(Municipality.municipality_name)
        )
        return list(result.scalars().all())
