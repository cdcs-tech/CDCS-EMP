"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Domain

Purchase order model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class PurchaseOrder(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents the formal Procurement/Purchasing commitment
    issued to a Supplier.
    """

    __tablename__ = "purchase_orders"

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "suppliers.id",
        ),
        nullable=False,
    )

    reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    order_date = db.Column(
        db.Date,
        nullable=False,
    )

    expected_delivery_date = db.Column(
        db.Date,
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    purchase_request_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "purchase_requests.id",
        ),
        nullable=False,
    )

    supplier = db.relationship(
        "Supplier",
        back_populates="purchase_orders",
        lazy="select",
    )

    purchase_request = db.relationship(
        "PurchaseRequest",
        back_populates="purchase_orders",
        lazy="select",
    )

    lines = db.relationship(
        "PurchaseOrderLine",
        back_populates="purchase_order",
        lazy="select",
    )


__all__ = [
    "PurchaseOrder",
]
