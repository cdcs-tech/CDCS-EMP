"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Inventory location domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class InventoryLocation(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a physical or logical location where
    inventory stock may be held.
    """

    __tablename__ = "inventory_locations"

    code = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    description = db.Column(
        db.String(500),
        nullable=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    balances = db.relationship(
        "StockBalance",
        back_populates="location",
        lazy="select",
    )

    movements = db.relationship(
        "StockMovement",
        back_populates="location",
        lazy="select",
    )

    source_transfers = db.relationship(
        "StockTransfer",
        foreign_keys="StockTransfer.source_location_id",
        back_populates="source_location",
        lazy="select",
    )

    destination_transfers = db.relationship(
        "StockTransfer",
        foreign_keys="StockTransfer.destination_location_id",
        back_populates="destination_location",
        lazy="select",
    )


__all__ = [
    "InventoryLocation",
]
