from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy import String, Text, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Conversation(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    participants_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Message(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # user/system/assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Use a safe attribute name to avoid clashing with SQLAlchemy Declarative .metadata
    meta_data: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")


class Document(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Embedding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "embeddings"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    vector: Mapped[str] = mapped_column(Text, nullable=False)  # store as JSON/text for portability; vector DB preferred
    # Preserve DB column name 'metadata' while using attribute 'meta_data'
    meta_data: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    document: Mapped["Document"] = relationship("Document")
