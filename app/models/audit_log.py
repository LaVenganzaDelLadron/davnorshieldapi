from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User

class AuditLog(UUIDMixin, Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    device: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User | None"] = relationship("User", back_populates="audit_logs")

