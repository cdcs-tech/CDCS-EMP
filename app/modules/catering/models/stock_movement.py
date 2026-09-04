"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Stock movement domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class StockMovement(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an immutable business record of a stock
    quantity change.
    """

    __tablename__ = "stock_movements"

    stock_item_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stock_items.id",
        ),
        nullable=False,
    )

    location_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "inventory_locations.id",
        ),
        nullable=False,
    )

    movement_type = db.Column(
        db.String(30),
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
        nullable=True,
    )

    reason = db.Column(
        db.String(500),
        nullable=True,
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

    transfer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stock_transfers.id",
        ),
        nullable=True,
    )

    stock_item = db.relationship(
        "StockItem",
        back_populates="movements",
        lazy="select",
    )

    location = db.relationship(
        "InventoryLocation",
        back_populates="movements",
        lazy="select",
    )

    transfer = db.relationship(
        "StockTransfer",
        back_populates="movements",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity <> 0",
            name="ck_stock_movements_quantity_nonzero",
        ),
        db.CheckConstraint(
            "movement_type IN "
            "('OPENING_BALANCE', 'RECEIPT', 'ISSUE', "
            "'ADJUSTMENT', 'TRANSFER')",
            name="ck_stock_movements_type",
        ),
        db.CheckConstraint(
            "status IN ('DRAFT', 'POSTED')",
            name="ck_stock_movements_status",
        ),
    )


__all__ = [
    "StockMovement",
]
