"""School schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchoolStatsResponse(BaseModel):
    """API response for school cyber-awareness stats."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    municipality_id: UUID
    school_name: str = Field(min_length=1, max_length=255)
    awareness_score: float
    reports_count: int
    phishing_attempts: int
    updated_at: datetime

