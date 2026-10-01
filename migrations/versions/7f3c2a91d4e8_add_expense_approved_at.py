"""Add approved_at to expenses.

Revision ID: 7f3c2a91d4e8
Revises: 304206a17fa5
Create Date: 2026-09-30
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f3c2a91d4e8"
down_revision = "304206a17fa5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add the Expense approval timestamp."""
    op.add_column(
        "expenses",
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove the Expense approval timestamp."""
    op.drop_column(
        "expenses",
        "approved_at",
    )
