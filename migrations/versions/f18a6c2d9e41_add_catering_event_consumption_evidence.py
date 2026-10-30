"""Add physical-consumption evidence for Catering Event Requirements.

Revision ID: f18a6c2d9e41
Revises: c3d9e71a4b62
Create Date: 2026-10-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision = "f18a6c2d9e41"
down_revision = "c3d9e71a4b62"
branch_labels = None
depends_on = None


def upgrade():
    """Create Event Requirement physical-consumption evidence."""

    op.create_table(
        "catering_event_consumption_evidence",
        sa.Column("event_requirement_id", sa.Integer(), nullable=False),
        sa.Column("stock_movement_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=3), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_catering_event_consumption_evidence_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["event_requirement_id"],
            ["catering_event_requirements.id"],
            name=(
                "fk_catering_event_consumption_evidence_event_requirement_id_"
                "catering_event_requirements"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["stock_movement_id"],
            ["stock_movements.id"],
            name=(
                "fk_catering_event_consumption_evidence_stock_movement_id_"
                "stock_movements"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_catering_event_consumption_evidence",
        ),
        sa.UniqueConstraint(
            "guid",
            name="uq_catering_event_consumption_evidence_guid",
        ),
        sa.UniqueConstraint(
            "stock_movement_id",
            name="uq_catering_event_consumption_evidence_stock_movement_id",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_catering_event_consumption_evidence_idempotency_key",
        ),
    )

    op.create_index(
        "ix_catering_event_consumption_evidence_event_requirement_id",
        "catering_event_consumption_evidence",
        ["event_requirement_id"],
        unique=False,
    )


def downgrade():
    """Drop Catering Event physical-consumption evidence."""

    op.drop_index(
        "ix_catering_event_consumption_evidence_event_requirement_id",
        table_name="catering_event_consumption_evidence",
    )
    op.drop_table("catering_event_consumption_evidence")
