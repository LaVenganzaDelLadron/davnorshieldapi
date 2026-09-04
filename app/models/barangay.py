"""Barangay model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.municipality import Municipality
    from app.models.scam_report import ScamReport
    from app.models.user import User


class Barangay(UUIDMixin, Base):
    """Barangay within a municipality."""

    __tablename__ = "barangays"

    barangay_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    municipality_id: Mapped[UUID] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    municipality: Mapped["Municipality"] = relationship(
        "Municipality",
        back_populates="barangays",
    )
    reports: Mapped[list["ScamReport"]] = relationship(
        "ScamReport",
        back_populates="barangay",
        cascade="all, delete-orphan",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="barangay",
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="barangay",
    )
