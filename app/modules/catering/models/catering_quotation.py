"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering quotation model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringQuotation(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a commercial quotation prepared by Catering for a
    Catering Event.

    The quotation is a Catering-owned commercial document. Invoices,
    payments, receivables, financial transactions, and general-ledger
    effects remain outside this model's ownership boundary.
    """

    __tablename__ = "catering_quotations"

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "customers.id",
        ),
        nullable=False,
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "catering_events.id",
        ),
        nullable=False,
    )

    quotation_date = db.Column(
        db.Date,
        nullable=False,
    )

    valid_until = db.Column(
        db.Date,
        nullable=False,
    )

    adjustment_amount = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=False,
        default=0,
    )

    subtotal = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=False,
        default=0,
    )

    total_amount = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=False,
        default=0,
    )

    customer_notes = db.Column(
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
        back_populates="quotations",
        lazy="select",
    )

    event = db.relationship(
        "CateringEvent",
        back_populates="quotations",
        lazy="select",
    )

    lines = db.relationship(
        "CateringQuotationLine",
        back_populates="quotation",
        lazy="select",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint(
            "valid_until >= quotation_date",
            name="ck_catering_quotations_valid_until",
        ),
        db.CheckConstraint(
            "status IN ("
            "'DRAFT', "
            "'ISSUED', "
            "'ACCEPTED', "
            "'DECLINED', "
            "'EXPIRED'"
            ")",
            name="ck_catering_quotations_status",
        ),
    )


__all__ = [
    "CateringQuotation",
]
