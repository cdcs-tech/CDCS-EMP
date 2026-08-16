"""
CDCS Enterprise Management Platform (CDCS-EMP)

Tenant Model
"""

from app.extensions import db

from .base import BaseModel
from .mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class Tenant(
    BaseModel,
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
):
    """
    Represents an isolated tenant within CDCS-EMP.

    A tenant represents a customer, deployment boundary,
    or independent business environment.
    """

    __tablename__ = "tenants"

    code = db.Column(
        db.String(50),
        unique=True,
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

    organizations = db.relationship(
        "Organization",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Tenant("
            f"code='{self.code}', "
            f"name='{self.name}'"
            f")>"
        )
