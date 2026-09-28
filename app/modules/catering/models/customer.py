"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Customer model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class Customer(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a customer receiving Catering services.

    Customers may be individuals or organizations.

    Financial accounts, invoices, payments, and other
    financial-treatment information are intentionally
    outside this model.
    """

    __tablename__ = "customers"

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    customer_type = db.Column(
        db.String(50),
        nullable=False,
    )

    phone = db.Column(
        db.String(50),
        nullable=True,
    )

    email = db.Column(
        db.String(150),
        nullable=True,
    )

    address = db.Column(
        db.String(500),
        nullable=True,
    )

    notes = db.Column(
        db.String(1000),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE",
    )

    requests = db.relationship(
        "CateringRequest",
        back_populates="customer",
        lazy="select",
    )

    events = db.relationship(
        "CateringEvent",
        back_populates="customer",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "customer_type IN ('INDIVIDUAL', 'ORGANIZATION')",
            name="ck_customers_customer_type",
        ),
        db.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_customers_status",
        ),
    )


__all__ = [
    "Customer",
]
