"""Scanner request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import ThreatCategory


class URLScanRequest(BaseModel):
    """Request payload for URL scanning."""

    model_config = ConfigDict(extra="forbid")

    url: HttpUrl


class SMSScanRequest(BaseModel):
    """Request payload for SMS scanning."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1)


class QRScanRequest(BaseModel):
    """Request payload for QR scanning."""

    model_config = ConfigDict(extra="forbid")

    qr_data: str = Field(min_length=1)


class ScanResponse(BaseModel):
    """Normalized scanner output."""

    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(ge=0, le=100)
    risk_level: str = Field(min_length=1, max_length=50)
    threat_category: ThreatCategory
    explanation: str
    recommendations: list[str]
