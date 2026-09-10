"""add procurement foundation

Revision ID: b917d20cd76a
Revises: 7491cd35c4bc
Create Date: 2026-09-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


# revision identifiers, used by Alembic.
revision = "b917d20cd76a"
down_revision = "7491cd35c4bc"
branch_labels = None
depends_on = None


def upgrade():
    """Create the Procurement foundation tables."""

    op.create_table(
        "suppliers",
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("supplier_type", sa.String(length=50), nullable=False),
        sa.Column("contact_information", sa.String(length=500), nullable=True),
        sa.Column("address_information", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
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
        "purchase_requirements",
        sa.Column("reference", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("source_module", sa.String(length=50), nullable=True),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("source_reference", sa.String(length=100), nullable=True),
        sa.Column("required_by_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
        sa.UniqueConstraint("guid"),
    )

    op.create_table(
        "purchase_requests",
        sa.Column("reference", sa.String(length=100), nullable=False),
        sa.Column("purchase_requirement_id", sa.Integer(), nullable=False),
        sa.Column("request_date", sa.Date(), nullable=False),
        sa.Column("required_by_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("justification", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["purchase_requirement_id"],
            ["purchase_requirements.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
        sa.UniqueConstraint("guid"),
    )

    op.create_table(
        "purchase_request_lines",
        sa.Column("purchase_request_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("item_reference", sa.String(length=100), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=18, scale=3), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("estimated_unit_cost", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("estimated_total", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("required_by_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["purchase_request_id"],
            ["purchase_requests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
    )

    op.create_table(
        "purchase_orders",
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("purchase_request_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["supplier_id"],
            ["suppliers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["purchase_request_id"],
            ["purchase_requests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
        sa.UniqueConstraint("guid"),
    )

    op.create_table(
        "purchase_order_lines",
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("item_reference", sa.String(length=100), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=18, scale=3), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.ForeignKeyConstraint(
            ["purchase_order_id"],
            ["purchase_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
    )


def downgrade():
    """Drop the Procurement foundation tables."""

    op.drop_table("purchase_order_lines")
    op.drop_table("purchase_orders")
    op.drop_table("purchase_request_lines")
    op.drop_table("purchase_requests")
    op.drop_table("purchase_requirements")
    op.drop_table("suppliers")
