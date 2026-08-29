"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain Models

Model foundation for the Catering business module.
"""

from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)

from .product import Product
from .product_category import ProductCategory

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    "ProductCategory",
    "Product",
]
