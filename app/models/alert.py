""""Alert models."""
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin
from app.models.enums import ALERT_LEVEL_ENUM, AlertLevel

if TYPE_CHECKING:
    from app.models.barangay import Barangay
    from app.models.municipality import Municipality
    from app.models.threat_pattern import ThreatPattern

class Alert(UUIDMixin, Base):
    __tablename__ = "alerts"

    threat_pattern_id: Mapped[UUID] = mapped_column(
        ForeignKey("threat_patterns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    municipality_id: Mapped[UUID] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    barangay_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("barangays.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    alert_level: Mapped[AlertLevel] = mapped_column(
        ALERT_LEVEL_ENUM,
        nullable=False,
        default=AlertLevel.low,
        server_default=text("'low'"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    threat_pattern: Mapped["ThreatPattern"] = relationship(
        "ThreatPattern",
        back_populates="alerts",
    )
    municipality: Mapped["Municipality"] = relationship(
        "Municipality",
        back_populates="alerts",
    )
    barangay: Mapped["Barangay | None"] = relationship(
        "Barangay",
        back_populates="alerts",
    )
