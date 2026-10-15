"""
Add stock allocations for Catering Event Requirements.

Revision ID: a6c2d8e41f70
Revises: 9b21afb06580
Create Date: 2026-10-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision = "a6c2d8e41f70"
down_revision = "9b21afb06580"
branch_labels = None
depends_on = None


def upgrade():
    """Create the Event Requirement stock allocation table."""

    op.create_table(
        "event_requirement_stock_allocations",
        sa.Column("event_requirement_id", sa.Integer(), nullable=False),
        sa.Column("stock_item_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 3), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_event_req_stock_alloc_quantity_positive",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'RELEASED')",
            name="ck_event_req_stock_alloc_status",
        ),
        sa.ForeignKeyConstraint(
            ["event_requirement_id"],
            ["catering_event_requirements.id"],
            name="fk_event_requirement_stock_allocations_event_requirement_id_catering_event_requirements",
        ),
        sa.ForeignKeyConstraint(
            ["stock_item_id"],
            ["stock_items.id"],
            name="fk_event_requirement_stock_allocations_stock_item_id_stock_items",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["inventory_locations.id"],
            name="fk_event_requirement_stock_allocations_location_id_inventory_locations",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_event_requirement_stock_allocations"),
        sa.UniqueConstraint(
            "guid",
            name="uq_event_requirement_stock_allocations_guid",
        ),
        sa.UniqueConstraint(
            "idempotency_key",
            name="uq_event_requirement_stock_allocations_idempotency_key",
        ),
    )

    op.create_index(
        "ix_event_requirement_stock_allocations_event_requirement_id",
        "event_requirement_stock_allocations",
        ["event_requirement_id"],
        unique=False,
    )
    op.create_index(
        "ix_event_requirement_stock_allocations_stock_item_id",
        "event_requirement_stock_allocations",
        ["stock_item_id"],
        unique=False,
    )
    op.create_index(
        "ix_event_requirement_stock_allocations_location_id",
        "event_requirement_stock_allocations",
        ["location_id"],
        unique=False,
    )


def downgrade():
    """Drop the Event Requirement stock allocation table."""

    op.drop_index(
        "ix_event_requirement_stock_allocations_location_id",
        table_name="event_requirement_stock_allocations",
    )
    op.drop_index(
        "ix_event_requirement_stock_allocations_stock_item_id",
        table_name="event_requirement_stock_allocations",
    )
    op.drop_index(
        "ix_event_requirement_stock_allocations_event_requirement_id",
        table_name="event_requirement_stock_allocations",
    )
    op.drop_table("event_requirement_stock_allocations")
