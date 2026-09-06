from __future__ import annotations
from collections.abc import Mapping
from uuid import UUID
from sqlalchemy import select
from app.models.school import School
from app.repositories.base import RepositoryBase


class SchoolRepository(RepositoryBase):
    """Database operations for school statistics."""

    async def get_school(self, school_id: UUID) -> School | None:
        """Fetch a school by UUID."""

        result = await self.db.execute(select(School).where(School.id == school_id))
        return result.scalar_one_or_none()

    async def update_awareness_score(self, school_id: UUID, score: float) -> School | None:
        """Update the awareness score for a school."""

        school = await self.get_school(school_id)
        if school is None:
            return None
        school.awareness_score = score
        await self.db.commit()
        await self.db.refresh(school)
        return school

    async def increment_reports(self, school_id: UUID, amount: int = 1) -> School | None:
        """Increment the school report counter."""

        school = await self.get_school(school_id)
        if school is None:
            return None
        school.reports_count += amount
        await self.db.commit()
        await self.db.refresh(school)
        return school

    async def list_schools(
        self,
        *,
        municipality_id: UUID | None = None,
    ) -> list[School]:
        """List schools, optionally constrained to a municipality."""

        stmt = select(School)
        if municipality_id is not None:
            stmt = stmt.where(School.municipality_id == municipality_id)
        stmt = stmt.order_by(School.school_name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

