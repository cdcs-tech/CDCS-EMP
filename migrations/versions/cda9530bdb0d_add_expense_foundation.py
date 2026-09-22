"""add expense foundation

Revision ID: cda9530bdb0d
Revises: d90e79d6deec
Create Date: 2026-09-22 02:44:36.359443

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


# revision identifiers, used by Alembic.

revision = "cda9530bdb0d"
down_revision = "d90e79d6deec"
branch_labels = None
depends_on = None


def upgrade():
    """Create the Expense Management foundation tables."""

    op.create_table(
        "expense_classifications",
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("guid"),
    )

    op.create_table(
        "expenses",
        sa.Column("classification_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=18, scale=2),
            nullable=False,
        ),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["classification_id"],
            ["expense_classifications.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
    )


def downgrade():
    """Drop the Expense Management foundation tables."""

    op.drop_table("expenses")
    op.drop_table("expense_classifications")
