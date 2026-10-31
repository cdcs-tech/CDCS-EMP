"""add nullable expense currency

Revision ID: f22bfca0cabd
Revises: f18a6c2d9e41
Create Date: 2026-10-31 03:40:43.203599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f22bfca0cabd'
down_revision = 'f18a6c2d9e41'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "expenses",
        sa.Column("currency", sa.String(length=3), nullable=True),
    )


def downgrade():
    op.drop_column("expenses", "currency")
