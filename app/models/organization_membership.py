"""
CDCS Enterprise Management Platform (CDCS-EMP)

Organization Membership Model
"""

from app.extensions import db

from .base import BaseModel
from .mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class OrganizationMembership(
    BaseModel,
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
):
    """
    Represents a user's membership in an organization.
    """

    __tablename__ = "organization_memberships"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    user = db.relationship(
        "User",
        back_populates="organization_memberships",
    )

    organization = db.relationship(
        "Organization",
        back_populates="memberships",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_user_organization_membership",
        ),
    )

    def __repr__(self):
        return (
            f"<OrganizationMembership("
            f"user_id={self.user_id}, "
            f"organization_id="
            f"{self.organization_id}"
            f")>"
        )
