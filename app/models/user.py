"""User model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import USER_ROLE_ENUM, UserRole

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.barangay import Barangay
    from app.models.municipality import Municipality
    from app.models.notification import Notification
    from app.models.scam_report import ScamReport


class User(UUIDMixin, TimestampMixin, Base):
    """Application account with RBAC metadata."""

    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        USER_ROLE_ENUM,
        nullable=False,
        default=UserRole.citizen,
        server_default=text("'citizen'"),
    )
    municipality_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("municipalities.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    barangay_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("barangays.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    municipality: Mapped["Municipality | None"] = relationship(
        "Municipality",
        back_populates="users",
    )
    barangay: Mapped["Barangay | None"] = relationship(
        "Barangay",
        back_populates="users",
    )
    reports: Mapped[list["ScamReport"]] = relationship(
        "ScamReport",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
