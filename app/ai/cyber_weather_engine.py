"""Cyber weather generation engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.constants import RiskLevel


@dataclass(slots=True)
class CyberWeatherAnalysis:
    """Cyber weather result."""

    risk_level: RiskLevel
    score: float
    recommendation: str


def generate_cyber_weather(
    *,
    phishing_reports: int,
    sms_reports: int,
    qr_reports: int,
    marketplace_reports: int,
    outbreak_count: int = 0,
    verified_alerts: int = 0,
    historical_trend: float = 0.0,
) -> CyberWeatherAnalysis:
    """Generate a cyber weather level from report and outbreak data."""

    score = (
        phishing_reports * 3.0
        + sms_reports * 2.0
        + qr_reports * 2.0
        + marketplace_reports * 3.0
        + outbreak_count * 8.0
        + verified_alerts * 4.0
        + historical_trend
    )
    score = round(min(score, 100.0), 2)
    if score >= 70:
        risk_level = RiskLevel.DANGEROUS
        recommendation = "Launch immediate public advisories and escalate monitoring."
    elif score >= 35:
        risk_level = RiskLevel.SUSPICIOUS
        recommendation = "Increase awareness campaigns and monitor report spikes."
    else:
        risk_level = RiskLevel.SAFE
        recommendation = "Maintain routine monitoring and regular education."
    return CyberWeatherAnalysis(risk_level=risk_level, score=score, recommendation=recommendation)

