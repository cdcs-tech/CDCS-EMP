"""add tenant and organization persistence

Revision ID: 8538697585d6
Revises: 1419ef8d0e4d
Create Date: 2026-09-04 02:04:32.036445

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


# revision identifiers, used by Alembic.
revision = "8538697585d6"
down_revision = "1419ef8d0e4d"
branch_labels = None
depends_on = None


def upgrade():
    """Create tenant and organization persistence tables."""

    op.create_table(
        "tenants",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
        sa.UniqueConstraint("code"),
    )

    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_tenants_code"),
            ["code"],
            unique=True,
        )
        batch_op.create_index(
            batch_op.f("ix_tenants_name"),
            ["name"],
            unique=False,
        )

    op.create_table(
        "organizations",
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
        sa.UniqueConstraint(
            "tenant_id",
            "code",
            name="uq_organization_tenant_code",
        ),
    )

    with op.batch_alter_table("organizations", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_organizations_code"),
            ["code"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_organizations_name"),
            ["name"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_organizations_tenant_id"),
            ["tenant_id"],
            unique=False,
        )

    op.create_table(
        "organization_memberships",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("guid", mssql.UNIQUEIDENTIFIER(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
        sa.UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_user_organization_membership",
        ),
    )

    with op.batch_alter_table(
        "organization_memberships",
        schema=None,
    ) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_organization_memberships_organization_id"),
            ["organization_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_organization_memberships_user_id"),
            ["user_id"],
            unique=False,
        )


def downgrade():
    """Remove tenant and organization persistence tables."""

    with op.batch_alter_table(
        "organization_memberships",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_organization_memberships_user_id")
        )
        batch_op.drop_index(
            batch_op.f("ix_organization_memberships_organization_id")
        )

    op.drop_table("organization_memberships")

    with op.batch_alter_table(
        "organizations",
        schema=None,
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f("ix_organizations_tenant_id")
        )
        batch_op.drop_index(
            batch_op.f("ix_organizations_name")
        )
        batch_op.drop_index(
            batch_op.f("ix_organizations_code")
        )

    op.drop_table("organizations")

    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_tenants_name"))
        batch_op.drop_index(batch_op.f("ix_tenants_code"))

    op.drop_table("tenants")
