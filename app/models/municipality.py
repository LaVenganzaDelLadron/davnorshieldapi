"""Municipality model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.barangay import Barangay
    from app.models.cyber_weather import CyberWeather
    from app.models.scam_report import ScamReport
    from app.models.school import School
    from app.models.user import User


class Municipality(UUIDMixin, Base):
    """Political municipality or city in Davao del Norte."""

    __tablename__ = "municipalities"

    municipality_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    province: Mapped[str] = mapped_column(String(255), nullable=False)

    barangays: Mapped[list["Barangay"]] = relationship(
        "Barangay",
        back_populates="municipality",
        cascade="all, delete-orphan",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="municipality",
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="municipality",
        cascade="all, delete-orphan",
    )
    reports: Mapped[list["ScamReport"]] = relationship(
        "ScamReport",
        back_populates="municipality",
    )
    weather_records: Mapped[list["CyberWeather"]] = relationship(
        "CyberWeather",
        back_populates="municipality",
        cascade="all, delete-orphan",
    )
    schools: Mapped[list["School"]] = relationship(
        "School",
        back_populates="municipality",
        cascade="all, delete-orphan",
    )
