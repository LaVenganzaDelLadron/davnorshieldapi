"""Scam report model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin
from app.models.enums import REPORT_STATUS_ENUM, THREAT_CATEGORY_ENUM, ReportStatus, ThreatCategory

if TYPE_CHECKING:
    from app.models.barangay import Barangay
    from app.models.municipality import Municipality
    from app.models.user import User


class ScamReport(UUIDMixin, Base):
    """Citizen-submitted scam report."""

    __tablename__ = "scam_reports"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    municipality_id: Mapped[UUID] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    barangay_id: Mapped[UUID] = mapped_column(
        ForeignKey("barangays.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    suspicious_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    qr_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    threat_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    threat_category: Mapped[ThreatCategory] = mapped_column(
        THREAT_CATEGORY_ENUM,
        nullable=False,
        index=True,
        default=ThreatCategory.other,
        server_default=text("'other'"),
    )
    status: Mapped[ReportStatus] = mapped_column(
        REPORT_STATUS_ENUM,
        nullable=False,
        default=ReportStatus.pending,
        server_default=text("'pending'"),
    )
    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="reports")
    municipality: Mapped["Municipality"] = relationship(
        "Municipality",
        back_populates="reports",
    )
    barangay: Mapped["Barangay"] = relationship("Barangay", back_populates="reports")
