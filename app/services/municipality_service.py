from __future__ import annotations
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.municipality import Municipality
from app.repositories.municipality_repository import MunicipalityRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.user_repository import UserRepository


class MunicipalityService:
    """Business logic for municipality read operations and summaries."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.municipalities = MunicipalityRepository(db)
        self.reports = ReportRepository(db)
        self.users = UserRepository(db)

    async def get_municipality(self, municipality_id: UUID) -> Municipality:
        """Return a municipality by UUID."""

        municipality = await self.municipalities.get_municipality(municipality_id)
        if municipality is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Municipality not found.")
        return municipality

    async def list_municipalities(self) -> list[Municipality]:
        """Return all municipalities."""

        return await self.municipalities.list_municipalities()

    async def create_municipality(self, data: dict[str, object]) -> Municipality:
        """Add an active Davao del Norte municipality or city."""

        self._validate_province(str(data["province"]))
        municipality = Municipality(**data)
        self.db.add(municipality)
        return await self._commit(municipality)

    async def update_municipality(
        self, municipality_id: UUID, data: dict[str, object]
    ) -> Municipality:
        """Update a municipality, including restoring a soft-deleted record."""

        municipality = await self.municipalities.get_municipality(
            municipality_id, include_inactive=True
        )
        if municipality is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Municipality not found.")
        if "province" in data:
            self._validate_province(str(data["province"]))
        for field, value in data.items():
            setattr(municipality, field, value)
        return await self._commit(municipality)

    async def deactivate_municipality(self, municipality_id: UUID) -> Municipality:
        """Soft-delete a municipality without removing its related records."""

        municipality = await self.municipalities.get_municipality(
            municipality_id, include_inactive=True
        )
        if municipality is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Municipality not found.")
        municipality.is_active = False
        return await self._commit(municipality)

    @staticmethod
    def _validate_province(province: str) -> None:
        if province.casefold().strip() != "davao del norte":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only municipalities in Davao del Norte are supported.",
            )

    async def _commit(self, municipality: Municipality) -> Municipality:
        try:
            await self.db.commit()
        except IntegrityError as error:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A municipality with that name already exists.",
            ) from error
        await self.db.refresh(municipality)
        return municipality

    async def get_summary(self) -> list[dict[str, object]]:
        """Return municipality summary statistics."""

        municipalities = await self.list_municipalities()
        summary: list[dict[str, object]] = []
        for municipality in municipalities:
            report_count = await self.reports.count_reports_by_municipality(municipality.id)
            users, _ = await self.users.list_users_by_municipality(
                municipality.id,
                page=1,
                size=10000,
            )
            summary.append(
                {
                    "id": str(municipality.id),
                    "municipality_name": municipality.municipality_name,
                    "province": municipality.province,
                    "report_count": report_count,
                    "user_count": len(users),
                }
            )
        return summary
