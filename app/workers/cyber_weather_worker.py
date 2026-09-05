"""Daily cyber weather generation worker."""

from __future__ import annotations

from app.database.session import AsyncSessionLocal
from app.repositories.municipality_repository import MunicipalityRepository
from app.services.weather_service import WeatherService


async def run_cyber_weather_job() -> dict[str, object]:
    """Generate cyber weather for every municipality."""

    async with AsyncSessionLocal() as db:
        municipalities = await MunicipalityRepository(db).list_municipalities()
        service = WeatherService(db)
        results = []
        for municipality in municipalities:
            weather_result = await service.generate_daily_weather(municipality.id)
            results.append(
                {
                    "municipality_id": str(municipality.id),
                    "risk_level": weather_result.weather.risk_level,
                    "score": weather_result.weather.total_reports,
                }
            )
        return {"processed": len(results), "results": results}

