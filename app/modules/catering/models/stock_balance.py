"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Stock balance domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class StockBalance(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents the current quantity of one Stock Item
    at one Inventory Location.
    """

    __tablename__ = "stock_balances"

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

    quantity = db.Column(
        db.Numeric(
            precision=18,
            scale=3,
        ),
        nullable=False,
        default=0,
    )

    stock_item = db.relationship(
        "StockItem",
        back_populates="balances",
        lazy="select",
    )

    location = db.relationship(
        "InventoryLocation",
        back_populates="balances",
        lazy="select",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "stock_item_id",
            "location_id",
            name="uq_stock_balance_item_location",
        ),
        db.CheckConstraint(
            "quantity >= 0",
            name="ck_stock_balances_quantity_nonnegative",
        ),
    )


__all__ = [
    "StockBalance",
]
