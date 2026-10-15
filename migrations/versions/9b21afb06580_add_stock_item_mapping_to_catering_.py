"""
Add stock item mapping to Catering Event Requirements.

Revision ID: 9b21afb06580
Revises: d6b4e9f2a731
Create Date: 2026-10-14 04:28:06.098390
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers used by Alembic.
revision = "9b21afb06580"
down_revision = "d6b4e9f2a731"
branch_labels = None
depends_on = None


def upgrade():
    """Add an optional StockItem relationship to EventRequirement."""

    op.add_column(
        "catering_event_requirements",
        sa.Column(
            "stock_item_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_catering_event_requirements_stock_item_id",
        "catering_event_requirements",
        "stock_items",
        ["stock_item_id"],
        ["id"],
    )


def downgrade():
    """Remove the optional StockItem relationship."""

    op.drop_constraint(
        "fk_catering_event_requirements_stock_item_id",
        "catering_event_requirements",
        type_="foreignkey",
    )

    op.drop_column(
        "catering_event_requirements",
        "stock_item_id",
    )
