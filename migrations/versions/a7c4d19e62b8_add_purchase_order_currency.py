"""Add nullable currency to purchase orders.

Revision ID: a7c4d19e62b8
Revises: f2a8c6d94170
"""

from alembic import op
import sqlalchemy as sa


revision = "a7c4d19e62b8"
down_revision = "f2a8c6d94170"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "purchase_orders",
        sa.Column("currency", sa.String(length=3), nullable=True),
    )


def downgrade():
    op.drop_column("purchase_orders", "currency")
