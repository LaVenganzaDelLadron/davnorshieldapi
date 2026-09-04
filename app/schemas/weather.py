"""Cyber weather schemas."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CyberWeatherResponse(BaseModel):
    """API response for a cyber weather snapshot."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    municipality_id: UUID
    risk_level: str = Field(min_length=1, max_length=50)
    phishing_reports: int
    sms_reports: int
    qr_reports: int
    marketplace_reports: int
    total_reports: int
    forecast_date: date

