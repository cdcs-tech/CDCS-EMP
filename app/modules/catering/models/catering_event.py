"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering Event model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringEvent(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents the operational Catering engagement created
    from an accepted or confirmed Catering Request.

    The Event provides the central operational context for
    downstream Catering capabilities while remaining outside
    Procurement, Inventory, Finance, and Reporting ownership.
    """

    __tablename__ = "catering_events"

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("catering_requests.id"),
        nullable=False,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
    )

    event_date = db.Column(
        db.Date,
        nullable=False,
    )

    service_details = db.Column(
        db.String(1000),
        nullable=False,
    )

    attendance = db.Column(
        db.Integer,
        nullable=False,
    )

    operational_notes = db.Column(
        db.String(1000),
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="REQUESTED",
    )

    request = db.relationship(
        "CateringRequest",
        back_populates="events",
        lazy="select",
    )

    customer = db.relationship(
        "Customer",
        back_populates="events",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "attendance > 0",
            name="ck_catering_events_attendance_positive",
        ),
        db.CheckConstraint(
            "status IN ("
            "'REQUESTED', "
            "'QUOTED', "
            "'PENDING_CONFIRMATION', "
            "'CONFIRMED', "
            "'PLANNING', "
            "'READY', "
            "'IN_PRODUCTION', "
            "'DELIVERED', "
            "'COMPLETED', "
            "'CANCELLED'"
            ")",
            name="ck_catering_events_status",
        ),
    )


__all__ = [
    "CateringEvent",
]
