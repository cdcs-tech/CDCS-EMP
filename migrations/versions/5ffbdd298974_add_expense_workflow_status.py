"""add expense workflow status

Revision ID: 5ffbdd298974
Revises: cda9530bdb0d
Create Date: 2026-09-23 21:39:40.945200

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = "5ffbdd298974"
down_revision = "cda9530bdb0d"
branch_labels = None
depends_on = None


def upgrade():
    """Add persisted workflow status to Expense records."""

    with op.batch_alter_table(
        "expenses",
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default=sa.text("'DRAFT'"),
            )
        )


def downgrade():
    """Remove persisted workflow status from Expense records."""

    with op.batch_alter_table(
        "expenses",
        schema=None,
    ) as batch_op:
        batch_op.drop_column("status")
