"""Barangay service."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.barangay import Barangay
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
