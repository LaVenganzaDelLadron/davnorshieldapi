"""Municipality routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.municipality_service import MunicipalityService

router = APIRouter(prefix="/municipalities", tags=["Municipalities"])


def _serialize_municipality(municipality) -> dict[str, object]:
    """Serialize a municipality ORM object."""

    return {
        "id": str(municipality.id),
        "municipality_name": municipality.municipality_name,
        "province": municipality.province,
    }


@router.get("/")
async def list_municipalities(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all municipalities."""

    municipalities = await MunicipalityService(db).list_municipalities()
    return [_serialize_municipality(item) for item in municipalities]


@router.get("/{municipality_id}")
async def get_municipality(
    municipality_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Return a municipality by UUID."""

    municipality = await MunicipalityService(db).get_municipality(municipality_id)
    return _serialize_municipality(municipality)


@router.get("/summary")
async def municipality_summary(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return municipality summary statistics."""

    return await MunicipalityService(db).get_summary()
