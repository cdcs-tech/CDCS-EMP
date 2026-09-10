"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Domain

Purchase request line model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class PurchaseRequestLine(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an individual procurement requirement within
    a PurchaseRequest.
    """

    __tablename__ = "purchase_request_lines"

    purchase_request_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "purchase_requests.id",
        ),
        nullable=False,
    )

    description = db.Column(
        db.String(500),
        nullable=False,
    )

    item_reference = db.Column(
        db.String(100),
        nullable=True,
    )

    quantity = db.Column(
        db.Numeric(
            precision=18,
            scale=3,
        ),
        nullable=False,
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
    )

    estimated_unit_cost = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=True,
    )

    estimated_total = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=True,
    )

    required_by_date = db.Column(
        db.Date,
        nullable=True,
    )

    notes = db.Column(
        db.String(1000),
        nullable=True,
    )

    purchase_request = db.relationship(
        "PurchaseRequest",
        back_populates="lines",
        lazy="select",
    )


__all__ = [
    "PurchaseRequestLine",
]
