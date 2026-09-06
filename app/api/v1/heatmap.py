from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app.services.heatmap_service import HeatmapService

router = APIRouter(prefix="/heatmap", tags=["Heatmap"])


@router.get("/municipality")
async def municipality_heatmap(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Return municipality heatmap data."""

    return {"items": await HeatmapService(db).municipality_statistics()}


@router.get("/barangay")
async def barangay_heatmap(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Return barangay heatmap data."""

    return {"items": await HeatmapService(db).barangay_statistics()}


@router.get("/statistics")
async def heatmap_statistics(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Return combined heatmap statistics."""

    return await HeatmapService(db).generate_heatmap()
