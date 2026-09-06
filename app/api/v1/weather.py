from __future__ import annotations
from typing import Annotated, Any
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_pagination
from app.schemas.weather import CyberWeatherResponse
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Cyber Weather"])


@router.get("/today", response_model=CyberWeatherResponse | None)
async def today_weather(
    municipality_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CyberWeatherResponse | None:
    """Return today's cyber weather for a municipality."""

    weather = await WeatherService(db).get_today_weather(municipality_id)
    return CyberWeatherResponse.model_validate(weather) if weather is not None else None


@router.get("/history")
async def weather_history(
    municipality_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return cyber weather history for a municipality."""

    service = WeatherService(db)
    items = await service.get_history(municipality_id, limit=pagination.size)
    return {
        "items": [CyberWeatherResponse.model_validate(item) for item in items],
        "page": pagination.page,
        "size": pagination.size,
        "total": len(items),
    }


@router.get("/municipality/{municipality_id}", response_model=CyberWeatherResponse | None)
async def municipality_weather(
    municipality_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CyberWeatherResponse | None:
    """Return the latest cyber weather record for a municipality."""

    weather = await WeatherService(db).get_municipality_weather(municipality_id)
    return CyberWeatherResponse.model_validate(weather) if weather is not None else None
