"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering Request model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringRequest(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an initial customer request for Catering services.

    A Catering Request captures customer demand before a confirmed
    operational commitment exists.

    Quotation, confirmation, procurement, inventory, production,
    delivery, revenue, and expense processing are handled by their
    respective domain capabilities and are intentionally outside
    this model.
    """

    __tablename__ = "catering_requests"

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
    )

    request_date = db.Column(
        db.Date,
        nullable=False,
    )

    requested_service = db.Column(
        db.String(150),
        nullable=False,
    )

    service_date = db.Column(
        db.Date,
        nullable=False,
    )

    attendance = db.Column(
        db.Integer,
        nullable=False,
    )

    requirements = db.Column(
        db.String(1000),
        nullable=True,
    )

    notes = db.Column(
        db.String(1000),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    customer = db.relationship(
        "Customer",
        back_populates="requests",
        lazy="select",
    )

    events = db.relationship(
        "CateringEvent",
        back_populates="request",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "attendance > 0",
            name="ck_catering_requests_attendance_positive",
        ),
        db.CheckConstraint(
            "status IN ('DRAFT', 'SUBMITTED', 'CANCELLED')",
            name="ck_catering_requests_status",
        ),
    )


__all__ = [
    "CateringRequest",
]
