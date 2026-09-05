"""Barangay routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.barangay_service import BarangayService

router = APIRouter(prefix="/barangays", tags=["Barangays"])


def _serialize_barangay(barangay) -> dict[str, object]:
    """Serialize a barangay ORM object."""

    return {
        "id": str(barangay.id),
        "barangay_name": barangay.barangay_name,
        "municipality_id": str(barangay.municipality_id),
    }


@router.get("/")
async def list_barangays(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all barangays."""

    barangays = await BarangayService(db).list_barangays()
    return [_serialize_barangay(barangay) for barangay in barangays]


@router.get("/{barangay_id}")
async def get_barangay(
    barangay_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Return a barangay by UUID."""

    barangay = await BarangayService(db).get_barangay(barangay_id)
    return _serialize_barangay(barangay)


@router.get("/municipality/{municipality_id}")
async def list_barangays_by_municipality(
    municipality_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return barangays for a municipality."""

    barangays = await BarangayService(db).list_barangays_by_municipality(municipality_id)
    return [_serialize_barangay(barangay) for barangay in barangays]
