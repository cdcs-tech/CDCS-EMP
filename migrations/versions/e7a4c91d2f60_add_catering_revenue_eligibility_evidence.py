"""Add evidence fields for Catering revenue eligibility.

Revision ID: e7a4c91d2f60
Revises: 4c91e7a2d6f3
Create Date: 2026-10-21
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers used by Alembic.
revision = "e7a4c91d2f60"
down_revision = "4c91e7a2d6f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add optional eligibility evidence to Catering revenue records."""

    op.add_column(
        "catering_revenues",
        sa.Column(
            "eligibility_quotation_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "catering_revenues",
        sa.Column(
            "delivery_evidence",
            sa.String(length=2000),
            nullable=True,
        ),
    )
    op.add_column(
        "catering_revenues",
        sa.Column(
            "eligibility_reason",
            sa.String(length=2000),
            nullable=True,
        ),
    )
    op.add_column(
        "catering_revenues",
        sa.Column(
            "amount_adjustment_reason",
            sa.String(length=2000),
            nullable=True,
        ),
    )
    op.add_column(
        "catering_revenues",
        sa.Column(
            "eligible_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_catering_revenues_eligibility_quotation",
        "catering_revenues",
        "catering_quotations",
        ["eligibility_quotation_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove the Catering revenue eligibility evidence fields."""

    op.drop_constraint(
        "fk_catering_revenues_eligibility_quotation",
        "catering_revenues",
        type_="foreignkey",
    )

    op.drop_column("catering_revenues", "eligible_at")
    op.drop_column("catering_revenues", "amount_adjustment_reason")
    op.drop_column("catering_revenues", "eligibility_reason")
    op.drop_column("catering_revenues", "delivery_evidence")
    op.drop_column("catering_revenues", "eligibility_quotation_id")
