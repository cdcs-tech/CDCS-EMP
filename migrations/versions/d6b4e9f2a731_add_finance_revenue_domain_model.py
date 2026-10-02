"""
Add Finance revenue domain model.

Revision ID: d6b4e9f2a731
Revises: c8e4f6a2b9d1
Create Date: 2026-10-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


# revision identifiers, used by Alembic.
revision = "d6b4e9f2a731"
down_revision = "c8e4f6a2b9d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the Finance revenue domain table."""

    op.create_table(
        "finance_revenues",
        sa.Column(
            "revenue_reference",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "contribution_reference",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "source_reference",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "revenue_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "revenue_classification",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "guid",
            mssql.UNIQUEIDENTIFIER(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
        sa.UniqueConstraint("revenue_reference"),
        sa.UniqueConstraint("contribution_reference"),
    )


def downgrade() -> None:
    """Remove the Finance revenue domain table."""

    op.drop_table("finance_revenues")
