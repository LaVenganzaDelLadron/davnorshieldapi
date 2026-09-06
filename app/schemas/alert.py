from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.enums import AlertLevel

class AlertResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    threat_pattern_id: UUID
    municipality_id: UUID
    barangay_id: UUID | None
    alert_level: AlertLevel
    title: str
    message: str
    is_active: bool
    created_at: datetime