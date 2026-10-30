"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Event physical-consumption evidence.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringEventConsumptionEvidence(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """Evidence linking a requirement to a posted physical stock issue."""

    __tablename__ = "catering_event_consumption_evidence"

    event_requirement_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "catering_event_requirements.id",
            name=(
                "fk_catering_event_consumption_evidence_event_requirement_id_"
                "catering_event_requirements"
            ),
        ),
        nullable=False,
    )

    stock_movement_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stock_movements.id",
            name=(
                "fk_catering_event_consumption_evidence_stock_movement_id_"
                "stock_movements"
            ),
        ),
        nullable=False,
        unique=True,
    )

    idempotency_key = db.Column(
        db.String(128),
        nullable=False,
        unique=True,
    )

    quantity = db.Column(
        db.Numeric(precision=18, scale=3),
        nullable=False,
    )

    unit = db.Column(db.String(50), nullable=False)

    event_requirement = db.relationship(
        "EventRequirement",
        lazy="select",
    )

    stock_movement = db.relationship(
        "StockMovement",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="ck_catering_event_consumption_evidence_quantity_positive",
        ),
    )


__all__ = ["CateringEventConsumptionEvidence"]
