"""Add Procurement business references to Inventory receipt idempotency.

Revision ID: 4c91e7a2d6f3
Revises: b358abf7b974
Create Date: 2026-10-18
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers used by Alembic.
revision = "4c91e7a2d6f3"
down_revision = "b358abf7b974"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "inventory_receipt_idempotency",
        sa.Column(
            "purchase_order_reference",
            sa.String(length=100),
            nullable=True,
        ),
    )
    op.add_column(
        "inventory_receipt_idempotency",
        sa.Column(
            "purchase_order_line_reference",
            sa.String(length=100),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_inventory_receipt_idempotency_po_line",
        "inventory_receipt_idempotency",
        [
            "purchase_order_reference",
            "purchase_order_line_reference",
        ],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_inventory_receipt_idempotency_po_line",
        table_name="inventory_receipt_idempotency",
    )
    op.drop_column(
        "inventory_receipt_idempotency",
        "purchase_order_line_reference",
    )
    op.drop_column(
        "inventory_receipt_idempotency",
        "purchase_order_reference",
    )
