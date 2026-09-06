"""Scope chat conversations to their authenticated owner.

Revision ID: 20260906_0002
Revises: 20260905_0001
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260906_0002"
down_revision = "20260905_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ownership to conversations for private-history isolation."""

    op.add_column(
        "conversations",
        sa.Column(
            "owner_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_conversations_owner_id",
        "conversations",
        ["owner_id"],
    )


def downgrade() -> None:
    """Remove conversation ownership."""

    op.drop_index("ix_conversations_owner_id", table_name="conversations")
    op.drop_column("conversations", "owner_id")
