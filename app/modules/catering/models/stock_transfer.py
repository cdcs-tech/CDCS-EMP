"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Stock transfer domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class StockTransfer(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents one business transaction transferring stock
    from one Inventory Location to another.
    """

    __tablename__ = "stock_transfers"

    stock_item_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stock_items.id",
        ),
        nullable=False,
    )

    source_location_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "inventory_locations.id",
        ),
        nullable=False,
    )

    destination_location_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "inventory_locations.id",
        ),
        nullable=False,
    )

    quantity = db.Column(
        db.Numeric(
            precision=18,
            scale=3,
        ),
        nullable=False,
    )

    reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    reason = db.Column(
        db.String(500),
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    occurred_at = db.Column(
        db.DateTime,
        nullable=False,
    )

    posted_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    stock_item = db.relationship(
        "StockItem",
        back_populates="transfers",
        lazy="select",
    )

    source_location = db.relationship(
        "InventoryLocation",
        foreign_keys=[source_location_id],
        back_populates="source_transfers",
        lazy="select",
    )

    destination_location = db.relationship(
        "InventoryLocation",
        foreign_keys=[destination_location_id],
        back_populates="destination_transfers",
        lazy="select",
    )

    movements = db.relationship(
        "StockMovement",
        back_populates="transfer",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="ck_stock_transfers_quantity_positive",
        ),
        db.CheckConstraint(
            "source_location_id <> destination_location_id",
            name="ck_stock_transfers_distinct_locations",
        ),
        db.CheckConstraint(
            "status IN ('DRAFT', 'POSTED')",
            name="ck_stock_transfers_status",
        ),
    )


__all__ = [
    "StockTransfer",
]
