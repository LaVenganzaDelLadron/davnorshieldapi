from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cyber_weather import CyberWeather
from app.models.enums import ThreatCategory
from app.repositories.report_repository import ReportRepository
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import CyberWeatherResponse
from app.utils.date_utils import today_date


@dataclass(slots=True)
class WeatherResult:
    """Result of a cyber weather computation."""

    weather: CyberWeather
    recommendations: list[str]


class WeatherService:
    """Generate daily cyber weather forecasts."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.weather = WeatherRepository(db)
        self.reports = ReportRepository(db)

    def _risk_level(
        self,
        *,
        phishing_reports: int,
        sms_reports: int,
        qr_reports: int,
        marketplace_reports: int,
    ) -> str:
        score = phishing_reports * 3 + sms_reports * 2 + qr_reports * 2 + marketplace_reports * 3
        if score >= 30:
            return "CRITICAL"
        if score >= 18:
            return "HIGH"
        if score >= 8:
            return "MEDIUM"
        return "LOW"

    def _recommendations(self, risk_level: str) -> list[str]:
        if risk_level == "CRITICAL":
            return [
                "Issue an urgent public advisory immediately.",
                "Increase monitoring and response cadence.",
                "Notify barangay and municipal administrators.",
            ]
        if risk_level == "HIGH":
            return [
                "Increase awareness campaigns.",
                "Monitor suspicious links and SMS spikes.",
                "Prepare targeted notifications.",
            ]
        if risk_level == "MEDIUM":
            return [
                "Warn users to verify messages and URLs.",
                "Review recent reports for clustering.",
            ]
        return [
            "Maintain routine monitoring.",
            "Share general cyber hygiene reminders.",
        ]

    async def generate_daily_weather(
        self,
        municipality_id: UUID,
        *,
        phishing_reports: int | None = None,
        sms_reports: int | None = None,
        qr_reports: int | None = None,
        marketplace_reports: int | None = None,
    ) -> WeatherResult:
        """Generate and store the daily cyber weather for a municipality."""

        phishing = phishing_reports if phishing_reports is not None else await self.reports.count_reports_by_municipality(
            municipality_id,
            threat_category=ThreatCategory.phishing,
        )
        sms = sms_reports if sms_reports is not None else await self.reports.count_reports_by_municipality(
            municipality_id,
            threat_category=ThreatCategory.sms_scam,
        )
        qr = qr_reports if qr_reports is not None else await self.reports.count_reports_by_municipality(
            municipality_id,
            threat_category=ThreatCategory.qr_scam,
        )
        marketplace = marketplace_reports if marketplace_reports is not None else await self.reports.count_reports_by_municipality(
            municipality_id,
            threat_category=ThreatCategory.marketplace_scam,
        )
        total = phishing + sms + qr + marketplace
        risk_level = self._risk_level(
            phishing_reports=phishing,
            sms_reports=sms,
            qr_reports=qr,
            marketplace_reports=marketplace,
        )
        existing = await self.weather.get_today_weather(municipality_id)
        payload = {
            "municipality_id": municipality_id,
            "risk_level": risk_level,
            "phishing_reports": phishing,
            "sms_reports": sms,
            "qr_reports": qr,
            "marketplace_reports": marketplace,
            "total_reports": total,
            "forecast_date": today_date(),
        }
        if existing is not None:
            updated = await self.weather.update_weather(existing.id, payload)
            if updated is None:
                raise RuntimeError("Unable to update weather record.")
            weather = updated
        else:
            weather = await self.weather.create_weather_record(payload)
        recommendations = self._recommendations(risk_level)
        return WeatherResult(weather=weather, recommendations=recommendations)

    async def generate_cyber_weather(
        self,
        municipality_id: UUID,
        *,
        phishing_reports: int | None = None,
        sms_reports: int | None = None,
        qr_reports: int | None = None,
        marketplace_reports: int | None = None,
    ) -> WeatherResult:
        """Backward-compatible alias for daily cyber weather generation."""

        return await self.generate_daily_weather(
            municipality_id,
            phishing_reports=phishing_reports,
            sms_reports=sms_reports,
            qr_reports=qr_reports,
            marketplace_reports=marketplace_reports,
        )

    async def get_weather_response(self, municipality_id: UUID) -> CyberWeatherResponse | None:
        """Return the latest weather response schema for a municipality."""

        weather = await self.weather.get_municipality_weather(municipality_id)
        if weather is None:
            return None
        return CyberWeatherResponse.model_validate(weather)

    async def get_today_weather(self, municipality_id: UUID) -> CyberWeather | None:
        """Return today's weather record."""

        return await self.weather.get_today_weather(municipality_id)

    async def get_history(self, municipality_id: UUID, *, limit: int = 30) -> list[CyberWeather]:
        """Return weather history for a municipality."""

        return await self.weather.get_weather_history(municipality_id, limit=limit)

    async def get_municipality_weather(self, municipality_id: UUID) -> CyberWeather | None:
        """Return the latest weather record for a municipality."""

        return await self.weather.get_municipality_weather(municipality_id)
