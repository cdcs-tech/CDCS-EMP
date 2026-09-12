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
# Purchase Requirement Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PURCHASE_REQUIREMENT_CREATE = Permission(
    code="PROCUREMENT.PURCHASE_REQUIREMENT.CREATE",
    name="procurement.purchase_requirement.create",
    description="Create Procurement purchase requirements.",
    module="PROCUREMENT",
    resource="purchase_requirement",
    action="create",
)

PROCUREMENT_PURCHASE_REQUIREMENT_READ = Permission(
    code="PROCUREMENT.PURCHASE_REQUIREMENT.READ",
    name="procurement.purchase_requirement.read",
    description="Read Procurement purchase requirements.",
    module="PROCUREMENT",
    resource="purchase_requirement",
    action="read",
)

PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE = Permission(
    code="PROCUREMENT.PURCHASE_REQUIREMENT.UPDATE",
    name="procurement.purchase_requirement.update",
    description="Update Procurement purchase requirements.",
    module="PROCUREMENT",
    resource="purchase_requirement",
    action="update",
)

PROCUREMENT_PURCHASE_REQUIREMENT_DELETE = Permission(
    code="PROCUREMENT.PURCHASE_REQUIREMENT.DELETE",
    name="procurement.purchase_requirement.delete",
    description="Delete Procurement purchase requirements.",
    module="PROCUREMENT",
    resource="purchase_requirement",
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
    PROCUREMENT_PURCHASE_REQUIREMENT_CREATE,
    PROCUREMENT_PURCHASE_REQUIREMENT_READ,
    PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE,
    PROCUREMENT_PURCHASE_REQUIREMENT_DELETE,
)


__all__ = [
    "PROCUREMENT_SUPPLIER_CREATE",
    "PROCUREMENT_SUPPLIER_READ",
    "PROCUREMENT_SUPPLIER_UPDATE",
    "PROCUREMENT_SUPPLIER_DELETE",
    "PROCUREMENT_PURCHASE_REQUIREMENT_CREATE",
    "PROCUREMENT_PURCHASE_REQUIREMENT_READ",
    "PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE",
    "PROCUREMENT_PURCHASE_REQUIREMENT_DELETE",
    "PROCUREMENT_PERMISSIONS",
]
