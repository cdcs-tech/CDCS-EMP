"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Event Requirement stock allocation domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import AuditMixin, TimestampMixin


class EventRequirementStockAllocation(
    TimestampMixin,
    AuditMixin,
    BaseModel,
):
    """
    Records stock allocated to a specific Catering Event Requirement.

    Allocations reserve quantities for fulfilment tracking but do not
    create stock movements or change physical stock balances.

    Multiple active allocations may fulfil one requirement incrementally.
    Availability, requirement quantity limits, item/unit compatibility,
    and idempotent creation must be enforced by the allocation service.
    """

    __tablename__ = "event_requirement_stock_allocations"

    event_requirement_id = db.Column(
        db.Integer,
        db.ForeignKey("catering_event_requirements.id"),
        nullable=False,
        index=True,
    )

    stock_item_id = db.Column(
        db.Integer,
        db.ForeignKey("stock_items.id"),
        nullable=False,
        index=True,
    )

    location_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory_locations.id"),
        nullable=False,
        index=True,
    )

    quantity = db.Column(
        db.Numeric(precision=18, scale=3),
        nullable=False,
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
    )

    idempotency_key = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE",
    )

    event_requirement = db.relationship(
        "EventRequirement",
        lazy="select",
    )

    stock_item = db.relationship(
        "StockItem",
        lazy="select",
    )

    location = db.relationship(
        "InventoryLocation",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="ck_event_req_stock_alloc_quantity_positive",
        ),
        db.CheckConstraint(
            "status IN ('ACTIVE', 'RELEASED')",
            name="ck_event_req_stock_alloc_status",
        ),
    )


__all__ = ["EventRequirementStockAllocation"]
