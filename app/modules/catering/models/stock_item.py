"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Stock item domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class StockItem(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents inventory configuration for an existing
    Catering Product.
    """

    __tablename__ = "stock_items"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "products.id",
        ),
        nullable=False,
        unique=True,
    )

    minimum_level = db.Column(
        db.Numeric(
            precision=18,
            scale=3,
        ),
        nullable=True,
    )

    reorder_level = db.Column(
        db.Numeric(
            precision=18,
            scale=3,
        ),
        nullable=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    product = db.relationship(
        "Product",
        lazy="select",
    )

    balances = db.relationship(
        "StockBalance",
        back_populates="stock_item",
        lazy="select",
    )

    movements = db.relationship(
        "StockMovement",
        back_populates="stock_item",
        lazy="select",
    )

    transfers = db.relationship(
        "StockTransfer",
        back_populates="stock_item",
        lazy="select",
    )


__all__ = [
    "StockItem",
]
