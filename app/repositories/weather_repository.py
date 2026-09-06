from __future__ import annotations
from collections.abc import Mapping
from datetime import date
from uuid import UUID
from sqlalchemy import select
from app.models.cyber_weather import CyberWeather
from app.repositories.base import RepositoryBase
from app.utils.date_utils import today_date


class WeatherRepository(RepositoryBase):
    """Database operations for cyber weather records."""

    async def create_weather_record(self, weather_data: Mapping[str, object]) -> CyberWeather:
        """Create a cyber weather snapshot."""

        weather = CyberWeather(**self._mapping_data(weather_data))
        self.db.add(weather)
        await self.db.commit()
        await self.db.refresh(weather)
        return weather

    async def get_today_weather(self, municipality_id: UUID) -> CyberWeather | None:
        """Get today's weather snapshot for a municipality."""

        result = await self.db.execute(
            select(CyberWeather)
            .where(
                CyberWeather.municipality_id == municipality_id,
                CyberWeather.forecast_date == today_date(),
            )
            .order_by(CyberWeather.forecast_date.desc())
        )
        return result.scalar_one_or_none()

    async def update_weather(
        self,
        weather_id: UUID,
        update_data: Mapping[str, object],
    ) -> CyberWeather | None:
        """Update a weather record."""

        result = await self.db.execute(select(CyberWeather).where(CyberWeather.id == weather_id))
        weather = result.scalar_one_or_none()
        if weather is None:
            return None
        for key, value in self._mapping_data(update_data).items():
            if hasattr(weather, key):
                setattr(weather, key, value)
        await self.db.commit()
        await self.db.refresh(weather)
        return weather

    async def get_weather_history(
        self,
        municipality_id: UUID,
        *,
        limit: int = 30,
    ) -> list[CyberWeather]:
        """Return historical weather snapshots for a municipality."""

        result = await self.db.execute(
            select(CyberWeather)
            .where(CyberWeather.municipality_id == municipality_id)
            .order_by(CyberWeather.forecast_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_municipality_weather(self, municipality_id: UUID) -> CyberWeather | None:
        """Return the latest weather record for a municipality."""

        result = await self.db.execute(
            select(CyberWeather)
            .where(CyberWeather.municipality_id == municipality_id)
            .order_by(CyberWeather.forecast_date.desc())
        )
        return result.scalars().first()

