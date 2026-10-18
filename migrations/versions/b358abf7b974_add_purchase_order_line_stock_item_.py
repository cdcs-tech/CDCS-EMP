"""add purchase order line stock item reference

Revision ID: b358abf7b974
Revises: a6c2d8e41f70
Create Date: 2026-10-17 20:34:57.924989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b358abf7b974'
down_revision = 'a6c2d8e41f70'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "purchase_order_lines",
        sa.Column(
            "stock_item_reference",
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column(
        "purchase_order_lines",
        "stock_item_reference",
    )
