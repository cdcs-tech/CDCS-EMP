"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering revenue model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringRevenue(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an authoritative Catering revenue business fact.

    Eligibility evidence identifies the delivered service, its
    accepted commercial quotation, and the reason the revenue
    qualifies for explicit recognition.

    Finance representation, accounting treatment, invoices,
    receipts, payments, and other Finance-owned records remain
    outside this model's ownership boundary.
    """

    __tablename__ = "catering_revenues"

    revenue_reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    source_type = db.Column(
        db.String(50),
        nullable=False,
    )

    source_reference = db.Column(
        db.String(100),
        nullable=False,
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=True,
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("catering_events.id"),
        nullable=True,
    )

    customer = db.relationship(
        "Customer",
        foreign_keys=[customer_id],
        lazy="select",
    )

    event = db.relationship(
        "CateringEvent",
        foreign_keys=[event_id],
        lazy="select",
    )

    amount = db.Column(
        db.Numeric(precision=18, scale=2),
        nullable=False,
    )

    currency = db.Column(
        db.String(3),
        nullable=False,
    )

    revenue_date = db.Column(
        db.Date,
        nullable=False,
    )

    revenue_classification = db.Column(
        db.String(100),
        nullable=True,
    )

    # Evidence captured when establishing eligibility.
    # Nullable to preserve compatibility with existing records.
    eligibility_quotation_id = db.Column(
        db.Integer,
        db.ForeignKey("catering_quotations.id"),
        nullable=True,
    )

    delivery_evidence = db.Column(
        db.String(2000),
        nullable=True,
    )

    eligibility_reason = db.Column(
        db.String(2000),
        nullable=True,
    )

    amount_adjustment_reason = db.Column(
        db.String(2000),
        nullable=True,
    )

    eligible_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    recognized_at = db.Column(
        db.DateTime,
        nullable=True,
    )
