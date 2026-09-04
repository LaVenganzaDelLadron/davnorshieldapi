"""Scam report schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import ReportStatus, ThreatCategory


class ReportBase(BaseModel):
    """Shared report fields."""

    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    municipality_id: UUID
    barangay_id: UUID
    report_type: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    suspicious_url: HttpUrl | None = None
    phone_number: str | None = Field(default=None, max_length=32)
    qr_data: str | None = None
    screenshot_path: str | None = Field(default=None, max_length=512)
    threat_score: int = Field(default=0, ge=0)
    threat_category: ThreatCategory = ThreatCategory.other
    status: ReportStatus = ReportStatus.pending


class ReportCreate(ReportBase):
    """Payload for creating a scam report."""


class ReportUpdate(BaseModel):
    """Payload for partially updating a scam report."""

    model_config = ConfigDict(extra="forbid")

    municipality_id: UUID | None = None
    barangay_id: UUID | None = None
    report_type: str | None = Field(default=None, min_length=1, max_length=50)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    suspicious_url: HttpUrl | None = None
    phone_number: str | None = Field(default=None, max_length=32)
    qr_data: str | None = None
    screenshot_path: str | None = Field(default=None, max_length=512)
    threat_score: int | None = Field(default=None, ge=0)
    threat_category: ThreatCategory | None = None
    status: ReportStatus | None = None


class ReportResponse(BaseModel):
    """API representation of a scam report."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    user_id: UUID
    municipality_id: UUID
    barangay_id: UUID
    report_type: str
    title: str
    description: str
    suspicious_url: str | None
    phone_number: str | None
    qr_data: str | None
    screenshot_path: str | None
    threat_score: int
    threat_category: ThreatCategory
    status: ReportStatus
    reported_at: datetime


class ReportScannerResponse(BaseModel):
    """Summarized scan output for a report or file attachment."""

    model_config = ConfigDict(extra="forbid")

    report_id: UUID | None = None
    risk_score: float = Field(ge=0, le=100)
    threat_category: ThreatCategory
    explanation: str
    recommendations: list[str]

