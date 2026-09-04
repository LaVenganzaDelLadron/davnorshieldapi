"""Cyber weather model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.municipality import Municipality


class CyberWeather(UUIDMixin, Base):
    """Aggregated cyber risk forecast for a municipality."""

    __tablename__ = "cyber_weather"

    municipality_id: Mapped[UUID] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    phishing_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sms_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qr_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    marketplace_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    forecast_date: Mapped[date] = mapped_column(Date, nullable=False)

    municipality: Mapped["Municipality"] = relationship(
        "Municipality",
        back_populates="weather_records",
    )

