"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Domain

Supplier model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class Supplier(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a Procurement/Purchasing-owned supplier master.

    Financial settlement, banking, tax settlement, and other
    financial-treatment information are intentionally outside
    this model.
    """

    __tablename__ = "suppliers"

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    code = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    supplier_type = db.Column(
        db.String(50),
        nullable=False,
    )

    contact_information = db.Column(
        db.String(500),
        nullable=True,
    )

    address_information = db.Column(
        db.String(500),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE",
    )

    purchase_orders = db.relationship(
        "PurchaseOrder",
        back_populates="supplier",
        lazy="select",
    )


__all__ = [
    "Supplier",
]
