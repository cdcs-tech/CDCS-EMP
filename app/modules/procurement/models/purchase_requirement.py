"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Domain

Purchase requirement model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class PurchaseRequirement(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a Procurement-side record of a business need
    requiring procurement action.

    The originating business capability remains authoritative
    for the underlying business context.
    """

    __tablename__ = "purchase_requirements"

    reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.String(500),
        nullable=False,
    )

    source_module = db.Column(
        db.String(50),
        nullable=True,
    )

    source_type = db.Column(
        db.String(100),
        nullable=True,
    )

    source_reference = db.Column(
        db.String(100),
        nullable=True,
    )

    required_by_date = db.Column(
        db.Date,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    purchase_requests = db.relationship(
        "PurchaseRequest",
        back_populates="purchase_requirement",
        lazy="select",
    )


__all__ = [
    "PurchaseRequirement",
]
