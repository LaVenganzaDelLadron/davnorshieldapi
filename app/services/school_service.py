from __future__ import annotations
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.school import School
from app.repositories.report_repository import ReportRepository
from app.repositories.school_repository import SchoolRepository


class SchoolService:
    """Compute school safety metrics without exposing student data."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.schools = SchoolRepository(db)
        self.reports = ReportRepository(db)

    def compute_awareness_score(
        self,
        *,
        phishing_attempts: int,
        reports_count: int,
        baseline: float = 100.0,
    ) -> float:
        """Compute an awareness score between 0 and 100."""

        score = baseline - (phishing_attempts * 4.0) - (reports_count * 2.5)
        return round(max(0.0, min(score, 100.0)), 2)

    async def phishing_statistics(self, municipality_id: UUID | None = None) -> list[dict[str, object]]:
        """Return phishing-focused school statistics."""

        schools = await self.schools.list_schools(municipality_id=municipality_id)
        return [
            {
                "id": str(school.id),
                "school_name": school.school_name,
                "municipality_id": str(school.municipality_id),
                "phishing_attempts": school.phishing_attempts,
                "awareness_score": school.awareness_score,
            }
            for school in schools
        ]

    async def reports_statistics(self, municipality_id: UUID | None = None) -> list[dict[str, object]]:
        """Return report statistics for schools."""

        schools = await self.schools.list_schools(municipality_id=municipality_id)
        return [
            {
                "id": str(school.id),
                "school_name": school.school_name,
                "municipality_id": str(school.municipality_id),
                "reports_count": school.reports_count,
                "awareness_score": school.awareness_score,
            }
            for school in schools
        ]

    async def recompute_school_metrics(self, school_id: UUID) -> School | None:
        """Recompute and persist a school's awareness score."""

        school = await self.schools.get_school(school_id)
        if school is None:
            return None
        score = self.compute_awareness_score(
            phishing_attempts=school.phishing_attempts,
            reports_count=school.reports_count,
        )
        return await self.schools.update_awareness_score(school_id, score)

    async def get_school(self, school_id: UUID) -> School | None:
        """Return a school by UUID."""

        school = await self.schools.get_school(school_id)
        if school is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found.")
        return school

    async def list_schools(self, municipality_id: UUID | None = None) -> list[School]:
        """Return schools, optionally filtered by municipality."""

        return await self.schools.list_schools(municipality_id=municipality_id)

    async def update_awareness_score(self, school_id: UUID, awareness_score: float) -> School:
        """Update a school's awareness score."""

        school = await self.schools.update_awareness_score(school_id, awareness_score)
        if school is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found.")
        return school
