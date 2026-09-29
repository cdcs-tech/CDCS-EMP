"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering quotation line model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringQuotationLine(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an individual commercial item or service included
    in a Catering quotation.
    """

    __tablename__ = "catering_quotation_lines"

    quotation_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "catering_quotations.id",
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

    unit_price = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=False,
    )

    total_amount = db.Column(
        db.Numeric(
            precision=18,
            scale=2,
        ),
        nullable=False,
    )

    notes = db.Column(
        db.String(1000),
        nullable=True,
    )

    quotation = db.relationship(
        "CateringQuotation",
        back_populates="lines",
        lazy="select",
    )


__all__ = [
    "CateringQuotationLine",
]
