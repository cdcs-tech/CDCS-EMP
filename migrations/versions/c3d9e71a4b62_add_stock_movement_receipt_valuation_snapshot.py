"""Add immutable PO receipt valuation snapshot fields.

Revision ID: c3d9e71a4b62
Revises: a7c4d19e62b8
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = "c3d9e71a4b62"
down_revision = "a7c4d19e62b8"
branch_labels = None
depends_on = None


def upgrade():
    """Add nullable commercial evidence fields to stock movements."""
    op.add_column(
        "stock_movements",
        sa.Column("purchase_order_reference", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "stock_movements",
        sa.Column(
            "purchase_order_line_reference",
            sa.String(length=100),
            nullable=True,
        ),
    )
    op.add_column(
        "stock_movements",
        sa.Column("unit", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "stock_movements",
        sa.Column(
            "valuation_unit_price",
            sa.Numeric(precision=18, scale=2),
            nullable=True,
        ),
    )
    op.add_column(
        "stock_movements",
        sa.Column("valuation_currency", sa.String(length=3), nullable=True),
    )
    op.add_column(
        "stock_movements",
        sa.Column("valuation_price_basis", sa.String(length=50), nullable=True),
    )


def downgrade():
    """Remove the receipt valuation snapshot fields."""
    op.drop_column("stock_movements", "valuation_price_basis")
    op.drop_column("stock_movements", "valuation_currency")
    op.drop_column("stock_movements", "valuation_unit_price")
    op.drop_column("stock_movements", "unit")
    op.drop_column("stock_movements", "purchase_order_line_reference")
    op.drop_column("stock_movements", "purchase_order_reference")
