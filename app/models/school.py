from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.municipality import Municipality

class School(UUIDMixin, Base):
    __tablename__ = "schools"

    municipality_id: Mapped[UUID] = mapped_column(
        ForeignKey("municipalities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    school_name: Mapped[str] = mapped_column(String(255), nullable=False)
    awareness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    phishing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    municipality: Mapped["Municipality"] = relationship(
        "Municipality",
        back_populates="schools",
    )

