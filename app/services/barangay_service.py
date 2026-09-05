"""Barangay service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.barangay import Barangay
from app.models.alert import Alert
from app.models.scam_report import ScamReport
from app.models.user import User
from app.repositories.barangay_repository import BarangayRepository


class BarangayService:
    """Business logic for barangay read operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.barangays = BarangayRepository(db)

    async def get_barangay(self, barangay_id: UUID) -> Barangay | None:
        """Return a barangay by UUID."""

        barangay = await self.barangays.get_barangay(barangay_id)
        if barangay is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barangay not found.")
        return barangay

    async def list_barangays(self) -> list[Barangay]:
        """Return all barangays."""

        return await self.barangays.list_barangays()

    async def list_barangays_by_municipality(self, municipality_id: UUID) -> list[Barangay]:
        """Return barangays within a municipality."""

        return await self.barangays.list_barangays_by_municipality(municipality_id)

    async def create_barangay(self, data: dict[str, object]) -> Barangay:
        """Add a barangay to an active Davao del Norte municipality."""

        await self._require_active_municipality(UUID(str(data["municipality_id"])))
        barangay = Barangay(**data)
        self.db.add(barangay)
        return await self._commit(barangay)

    async def update_barangay(self, barangay_id: UUID, data: dict[str, object]) -> Barangay:
        """Edit a barangay or move it to another active municipality."""

        barangay = await self.barangays.get_barangay(barangay_id)
        if barangay is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barangay not found.")
        if "municipality_id" in data:
            await self._require_active_municipality(UUID(str(data["municipality_id"])))
        for field, value in data.items():
            setattr(barangay, field, value)
        return await self._commit(barangay)

    async def delete_barangay(self, barangay_id: UUID) -> None:
        """Delete an unused barangay; referenced data is never cascade-deleted here."""

        barangay = await self.barangays.get_barangay(barangay_id)
        if barangay is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barangay not found.")
        references = await self._reference_count(barangay_id)
        if references:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Barangay cannot be deleted while it is assigned to users, reports, or alerts.",
            )
        await self.db.delete(barangay)
        await self.db.commit()

    async def _require_active_municipality(self, municipality_id: UUID) -> None:
        from app.repositories.municipality_repository import MunicipalityRepository

        municipality = await MunicipalityRepository(self.db).get_municipality(municipality_id)
        if municipality is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Barangays must belong to an active Davao del Norte municipality.",
            )

    async def _reference_count(self, barangay_id: UUID) -> int:
        counts = await self.db.execute(
            select(
                select(func.count()).select_from(User).where(User.barangay_id == barangay_id).scalar_subquery(),
                select(func.count()).select_from(ScamReport).where(ScamReport.barangay_id == barangay_id).scalar_subquery(),
                select(func.count()).select_from(Alert).where(Alert.barangay_id == barangay_id).scalar_subquery(),
            )
        )
        return sum(int(value or 0) for value in counts.one())

    async def _commit(self, barangay: Barangay) -> Barangay:
        try:
            await self.db.commit()
        except IntegrityError as error:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That barangay already exists in the selected municipality.",
            ) from error
        await self.db.refresh(barangay)
        return barangay
