"""Add explicit valuation status to stock movements.

Revision ID: f2a8c6d94170
Revises: e7a4c91d2f60
"""

from alembic import op
import sqlalchemy as sa


revision = "f2a8c6d94170"
down_revision = "e7a4c91d2f60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Record whether stock movement valuation evidence applies."""

    op.add_column(
        "stock_movements",
        sa.Column(
            "valuation_status",
            sa.String(length=20),
            nullable=False,
            server_default="NOT_APPLICABLE",
        ),
    )

    op.create_check_constraint(
        "ck_stock_movements_valuation_status",
        "stock_movements",
        "valuation_status IN ('NOT_APPLICABLE', 'UNVALUED', 'VALUED')",
    )


def downgrade() -> None:
    """Remove stock movement valuation status."""

    op.drop_constraint(
        "ck_stock_movements_valuation_status",
        "stock_movements",
        type_="check",
    )
    op.drop_column("stock_movements", "valuation_status")
