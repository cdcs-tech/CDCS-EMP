"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Domain

Purchase request model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class PurchaseRequest(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents the central Procurement/Purchasing operational
    request used to satisfy a purchase requirement.
    """

    __tablename__ = "purchase_requests"

    reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    purchase_requirement_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "purchase_requirements.id",
        ),
        nullable=False,
    )

    request_date = db.Column(
        db.Date,
        nullable=False,
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

    justification = db.Column(
        db.String(500),
        nullable=True,
    )

    notes = db.Column(
        db.String(1000),
        nullable=True,
    )

    purchase_requirement = db.relationship(
        "PurchaseRequirement",
        back_populates="purchase_requests",
        lazy="select",
    )

    lines = db.relationship(
        "PurchaseRequestLine",
        back_populates="purchase_request",
        lazy="select",
    )

    purchase_orders = db.relationship(
        "PurchaseOrder",
        back_populates="purchase_request",
        lazy="select",
    )


__all__ = [
    "PurchaseRequest",
]
