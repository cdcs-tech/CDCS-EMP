"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Procurement permission definitions.
"""

from app.core.security import Permission


# ---------------------------------------------------------------------------
# Supplier Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_SUPPLIER_CREATE = Permission(
    code="PROCUREMENT.SUPPLIER.CREATE",
    name="procurement.supplier.create",
    description="Create Procurement suppliers.",
    module="PROCUREMENT",
    resource="supplier",
    action="create",
)

PROCUREMENT_SUPPLIER_READ = Permission(
    code="PROCUREMENT.SUPPLIER.READ",
    name="procurement.supplier.read",
    description="Read Procurement suppliers.",
    module="PROCUREMENT",
    resource="supplier",
    action="read",
)

PROCUREMENT_SUPPLIER_UPDATE = Permission(
    code="PROCUREMENT.SUPPLIER.UPDATE",
    name="procurement.supplier.update",
    description="Update Procurement suppliers.",
    module="PROCUREMENT",
    resource="supplier",
    action="update",
)

PROCUREMENT_SUPPLIER_DELETE = Permission(
    code="PROCUREMENT.SUPPLIER.DELETE",
    name="procurement.supplier.delete",
    description="Delete Procurement suppliers.",
    module="PROCUREMENT",
    resource="supplier",
    action="delete",
)


# ---------------------------------------------------------------------------
# Aggregate Procurement Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PERMISSIONS = (
    PROCUREMENT_SUPPLIER_CREATE,
    PROCUREMENT_SUPPLIER_READ,
    PROCUREMENT_SUPPLIER_UPDATE,
    PROCUREMENT_SUPPLIER_DELETE,
)


__all__ = [
    "PROCUREMENT_SUPPLIER_CREATE",
    "PROCUREMENT_SUPPLIER_READ",
    "PROCUREMENT_SUPPLIER_UPDATE",
    "PROCUREMENT_SUPPLIER_DELETE",
    "PROCUREMENT_PERMISSIONS",
]
