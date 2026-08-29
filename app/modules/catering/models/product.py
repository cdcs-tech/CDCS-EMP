"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product master-data model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class Product(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a reusable Catering product master record.
    """

    __tablename__ = "products"

    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "product_categories.id",
        ),
        nullable=False,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    code = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.String(500),
        nullable=True,
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    category = db.relationship(
        "ProductCategory",
        back_populates="products",
        lazy="select",
    )


__all__ = [
    "Product",
]
