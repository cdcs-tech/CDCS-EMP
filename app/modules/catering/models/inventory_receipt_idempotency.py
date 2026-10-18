"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Inventory receipt idempotency record.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class InventoryReceiptIdempotency(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Durable idempotency record for Inventory purchase-order receipts.

    Each idempotency key identifies one physical receipt operation
    and maps to exactly one successfully posted StockMovement.

    Procurement business references are optional so that receipt
    operations originating outside Procurement remain compatible.
    """

    __tablename__ = "inventory_receipt_idempotency"

    __table_args__ = (
        db.Index(
            "ix_inventory_receipt_idempotency_po_line",
            "purchase_order_reference",
            "purchase_order_line_reference",
        ),
    )

    idempotency_key = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )

    stock_movement_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "stock_movements.id",
        ),
        nullable=False,
        unique=True,
    )

    purchase_order_reference = db.Column(
        db.String(100),
        nullable=True,
    )

    purchase_order_line_reference = db.Column(
        db.String(100),
        nullable=True,
    )

    stock_movement = db.relationship(
        "StockMovement",
        lazy="select",
    )


__all__ = [
    "InventoryReceiptIdempotency",
]
