"""
CDCS Enterprise Management Platform (CDCS-EMP)

Organization Model
"""

from app.extensions import db

from .base import BaseModel
from .mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class Organization(
    BaseModel,
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
):
    """
    Represents an organization belonging to a tenant.
    """

    __tablename__ = "organizations"

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    code = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
        index=True,
    )

    description = db.Column(
        db.String(500),
        nullable=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    tenant = db.relationship(
        "Tenant",
        back_populates="organizations",
    )

    memberships = db.relationship(
        "OrganizationMembership",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tenant_id",
            "code",
            name="uq_organization_tenant_code",
        ),
    )

    def __repr__(self):
        return (
            f"<Organization("
            f"tenant_id={self.tenant_id}, "
            f"code='{self.code}', "
            f"name='{self.name}'"
            f")>"
        )
