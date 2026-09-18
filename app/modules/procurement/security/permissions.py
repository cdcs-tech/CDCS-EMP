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
# Purchase Request CRUD Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PURCHASE_REQUEST_CREATE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.CREATE",
    name="procurement.purchase_request.create",
    description="Create Procurement purchase requests.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="create",
)

PROCUREMENT_PURCHASE_REQUEST_READ = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.READ",
    name="procurement.purchase_request.read",
    description="Read Procurement purchase requests.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="read",
)

PROCUREMENT_PURCHASE_REQUEST_UPDATE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.UPDATE",
    name="procurement.purchase_request.update",
    description="Update Procurement purchase requests.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="update",
)

PROCUREMENT_PURCHASE_REQUEST_DELETE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.DELETE",
    name="procurement.purchase_request.delete",
    description="Delete Procurement purchase requests.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="delete",
)


# ---------------------------------------------------------------------------
# Purchase Request Line Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PURCHASE_REQUEST_LINE_CREATE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST_LINE.CREATE",
    name="procurement.purchase_request_line.create",
    module="PROCUREMENT",
    resource="purchase_request_line",
    action="create",
)

PROCUREMENT_PURCHASE_REQUEST_LINE_READ = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST_LINE.READ",
    name="procurement.purchase_request_line.read",
    module="PROCUREMENT",
    resource="purchase_request_line",
    action="read",
)

PROCUREMENT_PURCHASE_REQUEST_LINE_UPDATE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST_LINE.UPDATE",
    name="procurement.purchase_request_line.update",
    module="PROCUREMENT",
    resource="purchase_request_line",
    action="update",
)

PROCUREMENT_PURCHASE_REQUEST_LINE_DELETE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST_LINE.DELETE",
    name="procurement.purchase_request_line.delete",
    module="PROCUREMENT",
    resource="purchase_request_line",
    action="delete",
)


# ---------------------------------------------------------------------------
# Purchase Order CRUD Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PURCHASE_ORDER_CREATE = Permission(
    code="PROCUREMENT.PURCHASE_ORDER.CREATE",
    name="procurement.purchase_order.create",
    description="Create Procurement purchase orders.",
    module="PROCUREMENT",
    resource="purchase_order",
    action="create",
)

PROCUREMENT_PURCHASE_ORDER_READ = Permission(
    code="PROCUREMENT.PURCHASE_ORDER.READ",
    name="procurement.purchase_order.read",
    description="Read Procurement purchase orders.",
    module="PROCUREMENT",
    resource="purchase_order",
    action="read",
)

PROCUREMENT_PURCHASE_ORDER_UPDATE = Permission(
    code="PROCUREMENT.PURCHASE_ORDER.UPDATE",
    name="procurement.purchase_order.update",
    description="Update Procurement purchase orders.",
    module="PROCUREMENT",
    resource="purchase_order",
    action="update",
)

PROCUREMENT_PURCHASE_ORDER_DELETE = Permission(
    code="PROCUREMENT.PURCHASE_ORDER.DELETE",
    name="procurement.purchase_order.delete",
    description="Delete Procurement purchase orders.",
    module="PROCUREMENT",
    resource="purchase_order",
    action="delete",
)

# ---------------------------------------------------------------------------
# Purchase Order Line Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PURCHASE_ORDER_LINE_CREATE = Permission(
    code="PROCUREMENT.PURCHASE_ORDER_LINE.CREATE",
    name="procurement.purchase_order_line.create",
    description="Create Procurement purchase order lines.",
    module="PROCUREMENT",
    resource="purchase_order_line",
    action="create",
)

PROCUREMENT_PURCHASE_ORDER_LINE_READ = Permission(
    code="PROCUREMENT.PURCHASE_ORDER_LINE.READ",
    name="procurement.purchase_order_line.read",
    description="Read Procurement purchase order lines.",
    module="PROCUREMENT",
    resource="purchase_order_line",
    action="read",
)

PROCUREMENT_PURCHASE_ORDER_LINE_UPDATE = Permission(
    code="PROCUREMENT.PURCHASE_ORDER_LINE.UPDATE",
    name="procurement.purchase_order_line.update",
    description="Update Procurement purchase order lines.",
    module="PROCUREMENT",
    resource="purchase_order_line",
    action="update",
)

PROCUREMENT_PURCHASE_ORDER_LINE_DELETE = Permission(
    code="PROCUREMENT.PURCHASE_ORDER_LINE.DELETE",
    name="procurement.purchase_order_line.delete",
    description="Delete Procurement purchase order lines.",
    module="PROCUREMENT",
    resource="purchase_order_line",
    action="delete",
)


# ---------------------------------------------------------------------------
# Purchase Request Workflow Permissions
# ---------------------------------------------------------------------------

PROCUREMENT_PURCHASE_REQUEST_SUBMIT = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.SUBMIT",
    name="procurement.purchase_request.submit",
    description="Submit Procurement purchase requests for approval.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="submit",
)

PROCUREMENT_PURCHASE_REQUEST_APPROVE = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.APPROVE",
    name="procurement.purchase_request.approve",
    description="Approve submitted Procurement purchase requests.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="approve",
)

PROCUREMENT_PURCHASE_REQUEST_REJECT = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.REJECT",
    name="procurement.purchase_request.reject",
    description="Reject submitted Procurement purchase requests.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="reject",
)

PROCUREMENT_PURCHASE_REQUEST_RETURN = Permission(
    code="PROCUREMENT.PURCHASE_REQUEST.RETURN",
    name="procurement.purchase_request.return",
    description="Return submitted Procurement purchase requests to draft.",
    module="PROCUREMENT",
    resource="purchase_request",
    action="return",
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
    PROCUREMENT_PURCHASE_REQUEST_CREATE,
    PROCUREMENT_PURCHASE_REQUEST_READ,
    PROCUREMENT_PURCHASE_REQUEST_UPDATE,
    PROCUREMENT_PURCHASE_REQUEST_DELETE,
    PROCUREMENT_PURCHASE_REQUEST_SUBMIT,
    PROCUREMENT_PURCHASE_REQUEST_APPROVE,
    PROCUREMENT_PURCHASE_REQUEST_REJECT,
    PROCUREMENT_PURCHASE_REQUEST_RETURN,
    PROCUREMENT_PURCHASE_REQUEST_LINE_CREATE,
    PROCUREMENT_PURCHASE_REQUEST_LINE_READ,
    PROCUREMENT_PURCHASE_REQUEST_LINE_UPDATE,
    PROCUREMENT_PURCHASE_REQUEST_LINE_DELETE,
    PROCUREMENT_PURCHASE_ORDER_CREATE,
    PROCUREMENT_PURCHASE_ORDER_READ,
    PROCUREMENT_PURCHASE_ORDER_UPDATE,
    PROCUREMENT_PURCHASE_ORDER_DELETE,
    PROCUREMENT_PURCHASE_ORDER_LINE_CREATE,
    PROCUREMENT_PURCHASE_ORDER_LINE_READ,
    PROCUREMENT_PURCHASE_ORDER_LINE_UPDATE,
    PROCUREMENT_PURCHASE_ORDER_LINE_DELETE,
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
    "PROCUREMENT_PURCHASE_REQUEST_CREATE",
    "PROCUREMENT_PURCHASE_REQUEST_READ",
    "PROCUREMENT_PURCHASE_REQUEST_UPDATE",
    "PROCUREMENT_PURCHASE_REQUEST_DELETE",
    "PROCUREMENT_PURCHASE_REQUEST_SUBMIT",
    "PROCUREMENT_PURCHASE_REQUEST_APPROVE",
    "PROCUREMENT_PURCHASE_REQUEST_REJECT",
    "PROCUREMENT_PURCHASE_REQUEST_RETURN",
    "PROCUREMENT_PURCHASE_REQUEST_LINE_CREATE",
    "PROCUREMENT_PURCHASE_REQUEST_LINE_READ",
    "PROCUREMENT_PURCHASE_REQUEST_LINE_UPDATE",
    "PROCUREMENT_PURCHASE_REQUEST_LINE_DELETE",
    "PROCUREMENT_PURCHASE_ORDER_CREATE",
    "PROCUREMENT_PURCHASE_ORDER_READ",
    "PROCUREMENT_PURCHASE_ORDER_UPDATE",
    "PROCUREMENT_PURCHASE_ORDER_DELETE",
    "PROCUREMENT_PURCHASE_ORDER_LINE_CREATE",
    "PROCUREMENT_PURCHASE_ORDER_LINE_READ",
    "PROCUREMENT_PURCHASE_ORDER_LINE_UPDATE",
    "PROCUREMENT_PURCHASE_ORDER_LINE_DELETE",
    "PROCUREMENT_PERMISSIONS",
]
