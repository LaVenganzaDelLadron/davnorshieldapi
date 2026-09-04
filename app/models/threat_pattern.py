"""Threat pattern model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin
from app.models.enums import THREAT_CATEGORY_ENUM, ThreatCategory

if TYPE_CHECKING:
    from app.models.alert import Alert


class ThreatPattern(UUIDMixin, Base):
    """Detected malicious pattern aggregated from many reports."""

    __tablename__ = "threat_patterns"

    pattern_name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    threat_category: Mapped[ThreatCategory] = mapped_column(
        THREAT_CATEGORY_ENUM,
        nullable=False,
        index=True,
        default=ThreatCategory.other,
        server_default=text("'other'"),
    )
    malicious_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    malicious_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    keyword_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="threat_pattern",
    )
