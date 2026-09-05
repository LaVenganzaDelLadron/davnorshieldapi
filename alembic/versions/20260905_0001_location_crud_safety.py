"""Add safe location-management constraints.

Revision ID: 20260905_0001
Revises:
Create Date: 2026-09-05 00:01:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260905_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add municipality soft deletion and prevent duplicate local barangays."""

    op.add_column(
        "municipalities",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_unique_constraint(
        "uq_barangays_name_municipality",
        "barangays",
        ["barangay_name", "municipality_id"],
    )


def downgrade() -> None:
    """Remove location-management safeguards."""

    op.drop_constraint("uq_barangays_name_municipality", "barangays", type_="unique")
    op.drop_column("municipalities", "is_active")
