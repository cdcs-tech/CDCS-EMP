"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product category master-data model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class ProductCategory(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a category of products used by the
    Catering module.
    """

    __tablename__ = "product_categories"

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

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    products = db.relationship(
        "Product",
        back_populates="category",
        lazy="select",
    )


__all__ = [
    "ProductCategory",
]
