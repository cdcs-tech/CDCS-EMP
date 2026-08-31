"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Security permission definitions.
"""

from __future__ import annotations

from app.core.security import Permission


CATERING_PRODUCT_CATEGORY_CREATE = Permission(
    code="CATERING.PRODUCT_CATEGORY.CREATE",
    name="catering.product_category.create",
    description="Create Catering product categories.",
    module="CATERING",
    resource="product_category",
    action="create",
)

CATERING_PRODUCT_CATEGORY_READ = Permission(
    code="CATERING.PRODUCT_CATEGORY.READ",
    name="catering.product_category.read",
    description="View Catering product categories.",
    module="CATERING",
    resource="product_category",
    action="read",
)

CATERING_PRODUCT_CATEGORY_UPDATE = Permission(
    code="CATERING.PRODUCT_CATEGORY.UPDATE",
    name="catering.product_category.update",
    description="Update Catering product categories.",
    module="CATERING",
    resource="product_category",
    action="update",
)

CATERING_PRODUCT_CATEGORY_DELETE = Permission(
    code="CATERING.PRODUCT_CATEGORY.DELETE",
    name="catering.product_category.delete",
    description="Delete Catering product categories.",
    module="CATERING",
    resource="product_category",
    action="delete",
)


CATERING_PRODUCT_CREATE = Permission(
    code="CATERING.PRODUCT.CREATE",
    name="catering.product.create",
    description="Create Catering products.",
    module="CATERING",
    resource="product",
    action="create",
)

CATERING_PRODUCT_READ = Permission(
    code="CATERING.PRODUCT.READ",
    name="catering.product.read",
    description="View Catering products.",
    module="CATERING",
    resource="product",
    action="read",
)

CATERING_PRODUCT_UPDATE = Permission(
    code="CATERING.PRODUCT.UPDATE",
    name="catering.product.update",
    description="Update Catering products.",
    module="CATERING",
    resource="product",
    action="update",
)

CATERING_PRODUCT_DELETE = Permission(
    code="CATERING.PRODUCT.DELETE",
    name="catering.product.delete",
    description="Delete Catering products.",
    module="CATERING",
    resource="product",
    action="delete",
)


CATERING_PERMISSIONS = (
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
    CATERING_PRODUCT_CATEGORY_UPDATE,
    CATERING_PRODUCT_CATEGORY_DELETE,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
    CATERING_PRODUCT_UPDATE,
    CATERING_PRODUCT_DELETE,
)


__all__ = [
    "CATERING_PRODUCT_CATEGORY_CREATE",
    "CATERING_PRODUCT_CATEGORY_READ",
    "CATERING_PRODUCT_CATEGORY_UPDATE",
    "CATERING_PRODUCT_CATEGORY_DELETE",
    "CATERING_PRODUCT_CREATE",
    "CATERING_PRODUCT_READ",
    "CATERING_PRODUCT_UPDATE",
    "CATERING_PRODUCT_DELETE",
    "CATERING_PERMISSIONS",
]
