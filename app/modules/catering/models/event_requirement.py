"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering Event Requirement model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class EventRequirement(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an operational requirement of a Catering Event.

    The requirement remains owned by Catering and records the
    explicit fulfilment path without becoming a Procurement
    transaction or an Inventory stock transaction.
    """

    __tablename__ = "catering_event_requirements"

    event_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "catering_events.id",
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

    fulfilment_type = db.Column(
        db.String(20),
        nullable=False,
    )

    required_by_date = db.Column(
        db.Date,
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

    event = db.relationship(
        "CateringEvent",
        back_populates="requirements",
        lazy="select",
    )

    purchase_requirement = db.relationship(
        "CateringPurchaseRequirement",
        back_populates="event_requirement",
        uselist=False,
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="ck_catering_event_requirements_quantity_positive",
        ),
        db.CheckConstraint(
            "fulfilment_type IN ('INVENTORY', 'PROCUREMENT')",
            name="ck_catering_event_requirements_fulfilment_type",
        ),
        db.CheckConstraint(
            "status IN ('DRAFT', 'IDENTIFIED', 'READY', 'CANCELLED')",
            name="ck_catering_event_requirements_status",
        ),
    )


__all__ = [
    "EventRequirement",
]
