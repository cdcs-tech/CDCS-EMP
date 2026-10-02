"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering permission definitions.
"""

from app.core.security import Permission


# ---------------------------------------------------------------------------
# Product Category Permissions
# ---------------------------------------------------------------------------

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
    description="Read Catering product categories.",
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


# ---------------------------------------------------------------------------
# Product Permissions
# ---------------------------------------------------------------------------

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
    description="Read Catering products.",
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


# ---------------------------------------------------------------------------
# Inventory — Stock Item Permissions
# ---------------------------------------------------------------------------

CATERING_STOCK_ITEM_CREATE = Permission(
    code="CATERING.STOCK_ITEM.CREATE",
    name="catering.stock_item.create",
    description="Create Catering stock items.",
    module="CATERING",
    resource="stock_item",
    action="create",
)

CATERING_STOCK_ITEM_READ = Permission(
    code="CATERING.STOCK_ITEM.READ",
    name="catering.stock_item.read",
    description="Read Catering stock items.",
    module="CATERING",
    resource="stock_item",
    action="read",
)

CATERING_STOCK_ITEM_UPDATE = Permission(
    code="CATERING.STOCK_ITEM.UPDATE",
    name="catering.stock_item.update",
    description="Update Catering stock items.",
    module="CATERING",
    resource="stock_item",
    action="update",
)

CATERING_STOCK_ITEM_DELETE = Permission(
    code="CATERING.STOCK_ITEM.DELETE",
    name="catering.stock_item.delete",
    description="Delete Catering stock items.",
    module="CATERING",
    resource="stock_item",
    action="delete",
)


# ---------------------------------------------------------------------------
# Inventory — Location Permissions
# ---------------------------------------------------------------------------

CATERING_INVENTORY_LOCATION_CREATE = Permission(
    code="CATERING.INVENTORY_LOCATION.CREATE",
    name="catering.inventory_location.create",
    description="Create Catering inventory locations.",
    module="CATERING",
    resource="inventory_location",
    action="create",
)

CATERING_INVENTORY_LOCATION_READ = Permission(
    code="CATERING.INVENTORY_LOCATION.READ",
    name="catering.inventory_location.read",
    description="Read Catering inventory locations.",
    module="CATERING",
    resource="inventory_location",
    action="read",
)

CATERING_INVENTORY_LOCATION_UPDATE = Permission(
    code="CATERING.INVENTORY_LOCATION.UPDATE",
    name="catering.inventory_location.update",
    description="Update Catering inventory locations.",
    module="CATERING",
    resource="inventory_location",
    action="update",
)

CATERING_INVENTORY_LOCATION_DELETE = Permission(
    code="CATERING.INVENTORY_LOCATION.DELETE",
    name="catering.inventory_location.delete",
    description="Delete Catering inventory locations.",
    module="CATERING",
    resource="inventory_location",
    action="delete",
)


# ---------------------------------------------------------------------------
# Inventory — Stock Balance Permissions
# ---------------------------------------------------------------------------

CATERING_STOCK_BALANCE_READ = Permission(
    code="CATERING.STOCK_BALANCE.READ",
    name="catering.stock_balance.read",
    description="Read Catering stock balances.",
    module="CATERING",
    resource="stock_balance",
    action="read",
)


# ---------------------------------------------------------------------------
# Inventory — Stock Movement Permissions
# ---------------------------------------------------------------------------

CATERING_STOCK_MOVEMENT_CREATE = Permission(
    code="CATERING.STOCK_MOVEMENT.CREATE",
    name="catering.stock_movement.create",
    description="Create Catering stock movements.",
    module="CATERING",
    resource="stock_movement",
    action="create",
)

CATERING_STOCK_MOVEMENT_READ = Permission(
    code="CATERING.STOCK_MOVEMENT.READ",
    name="catering.stock_movement.read",
    description="Read Catering stock movements.",
    module="CATERING",
    resource="stock_movement",
    action="read",
)

CATERING_STOCK_MOVEMENT_POST = Permission(
    code="CATERING.STOCK_MOVEMENT.POST",
    name="catering.stock_movement.post",
    description="Post Catering stock movements.",
    module="CATERING",
    resource="stock_movement",
    action="post",
)


# ---------------------------------------------------------------------------
# Inventory — Stock Transfer Permissions
# ---------------------------------------------------------------------------

CATERING_STOCK_TRANSFER_CREATE = Permission(
    code="CATERING.STOCK_TRANSFER.CREATE",
    name="catering.stock_transfer.create",
    description="Create Catering stock transfers.",
    module="CATERING",
    resource="stock_transfer",
    action="create",
)

CATERING_STOCK_TRANSFER_READ = Permission(
    code="CATERING.STOCK_TRANSFER.READ",
    name="catering.stock_transfer.read",
    description="Read Catering stock transfers.",
    module="CATERING",
    resource="stock_transfer",
    action="read",
)

CATERING_STOCK_TRANSFER_POST = Permission(
    code="CATERING.STOCK_TRANSFER.POST",
    name="catering.stock_transfer.post",
    description="Post Catering stock transfers.",
    module="CATERING",
    resource="stock_transfer",
    action="post",
)


# ---------------------------------------------------------------------------
# Customer Permissions
# ---------------------------------------------------------------------------

CATERING_CUSTOMER_CREATE = Permission(
    code="CATERING.CUSTOMER.CREATE",
    name="catering.customer.create",
    description="Create Catering customers.",
    module="CATERING",
    resource="customer",
    action="create",
)

CATERING_CUSTOMER_READ = Permission(
    code="CATERING.CUSTOMER.READ",
    name="catering.customer.read",
    description="Read Catering customers.",
    module="CATERING",
    resource="customer",
    action="read",
)

CATERING_CUSTOMER_UPDATE = Permission(
    code="CATERING.CUSTOMER.UPDATE",
    name="catering.customer.update",
    description="Update Catering customers.",
    module="CATERING",
    resource="customer",
    action="update",
)

CATERING_CUSTOMER_DELETE = Permission(
    code="CATERING.CUSTOMER.DELETE",
    name="catering.customer.delete",
    description="Delete Catering customers.",
    module="CATERING",
    resource="customer",
    action="delete",
)


# ---------------------------------------------------------------------------
# Catering Request Permissions
# ---------------------------------------------------------------------------

CATERING_REQUEST_CREATE = Permission(
    code="CATERING.CATERING_REQUEST.CREATE",
    name="catering.catering_request.create",
    description="Create Catering requests.",
    module="CATERING",
    resource="catering_request",
    action="create",
)

CATERING_REQUEST_READ = Permission(
    code="CATERING.CATERING_REQUEST.READ",
    name="catering.catering_request.read",
    description="Read Catering requests.",
    module="CATERING",
    resource="catering_request",
    action="read",
)

CATERING_REQUEST_UPDATE = Permission(
    code="CATERING.CATERING_REQUEST.UPDATE",
    name="catering.catering_request.update",
    description="Update Catering requests.",
    module="CATERING",
    resource="catering_request",
    action="update",
)

CATERING_REQUEST_DELETE = Permission(
    code="CATERING.CATERING_REQUEST.DELETE",
    name="catering.catering_request.delete",
    description="Delete Catering requests.",
    module="CATERING",
    resource="catering_request",
    action="delete",
)

CATERING_REQUEST_SUBMIT = Permission(
    code="CATERING.CATERING_REQUEST.SUBMIT",
    name="catering.catering_request.submit",
    description="Submit Catering requests.",
    module="CATERING",
    resource="catering_request",
    action="submit",
)

CATERING_REQUEST_CANCEL = Permission(
    code="CATERING.CATERING_REQUEST.CANCEL",
    name="catering.catering_request.cancel",
    description="Cancel Catering requests.",
    module="CATERING",
    resource="catering_request",
    action="cancel",
)


# ---------------------------------------------------------------------------
# Catering Event Permissions
# ---------------------------------------------------------------------------

CATERING_EVENT_CREATE = Permission(
    code="CATERING.CATERING_EVENT.CREATE",
    name="catering.catering_event.create",
    description="Create Catering events.",
    module="CATERING",
    resource="catering_event",
    action="create",
)

CATERING_EVENT_READ = Permission(
    code="CATERING.CATERING_EVENT.READ",
    name="catering.catering_event.read",
    description="Read Catering events.",
    module="CATERING",
    resource="catering_event",
    action="read",
)

CATERING_EVENT_UPDATE = Permission(
    code="CATERING.CATERING_EVENT.UPDATE",
    name="catering.catering_event.update",
    description="Update Catering events.",
    module="CATERING",
    resource="catering_event",
    action="update",
)

CATERING_EVENT_DELETE = Permission(
    code="CATERING.CATERING_EVENT.DELETE",
    name="catering.catering_event.delete",
    description="Delete Catering events.",
    module="CATERING",
    resource="catering_event",
    action="delete",
)

CATERING_EVENT_QUOTE = Permission(
    code="CATERING.CATERING_EVENT.QUOTE",
    name="catering.catering_event.quote",
    description="Quote Catering events.",
    module="CATERING",
    resource="catering_event",
    action="quote",
)

CATERING_EVENT_CONFIRM = Permission(
    code="CATERING.CATERING_EVENT.CONFIRM",
    name="catering.catering_event.confirm",
    description="Confirm Catering events.",
    module="CATERING",
    resource="catering_event",
    action="confirm",
)

CATERING_EVENT_PLAN = Permission(
    code="CATERING.CATERING_EVENT.PLAN",
    name="catering.catering_event.plan",
    description="Plan Catering events.",
    module="CATERING",
    resource="catering_event",
    action="plan",
)

CATERING_EVENT_READY = Permission(
    code="CATERING.CATERING_EVENT.READY",
    name="catering.catering_event.ready",
    description="Mark Catering events ready.",
    module="CATERING",
    resource="catering_event",
    action="ready",
)

CATERING_EVENT_START_PRODUCTION = Permission(
    code="CATERING.CATERING_EVENT.START_PRODUCTION",
    name="catering.catering_event.start_production",
    description="Start production for Catering events.",
    module="CATERING",
    resource="catering_event",
    action="start_production",
)

CATERING_EVENT_DELIVER = Permission(
    code="CATERING.CATERING_EVENT.DELIVER",
    name="catering.catering_event.deliver",
    description="Deliver Catering events.",
    module="CATERING",
    resource="catering_event",
    action="deliver",
)

CATERING_EVENT_COMPLETE = Permission(
    code="CATERING.CATERING_EVENT.COMPLETE",
    name="catering.catering_event.complete",
    description="Complete Catering events.",
    module="CATERING",
    resource="catering_event",
    action="complete",
)

CATERING_EVENT_CANCEL = Permission(
    code="CATERING.CATERING_EVENT.CANCEL",
    name="catering.catering_event.cancel",
    description="Cancel Catering events.",
    module="CATERING",
    resource="catering_event",
    action="cancel",
)


# ---------------------------------------------------------------------------
# Catering Event Requirement Permissions
# ---------------------------------------------------------------------------

CATERING_EVENT_REQUIREMENT_CREATE = Permission(
    code="CATERING.EVENT_REQUIREMENT.CREATE",
    name="catering.event_requirement.create",
    description="Create Catering event requirements.",
    module="CATERING",
    resource="event_requirement",
    action="create",
)

CATERING_EVENT_REQUIREMENT_READ = Permission(
    code="CATERING.EVENT_REQUIREMENT.READ",
    name="catering.event_requirement.read",
    description="Read Catering event requirements.",
    module="CATERING",
    resource="event_requirement",
    action="read",
)

CATERING_EVENT_REQUIREMENT_UPDATE = Permission(
    code="CATERING.EVENT_REQUIREMENT.UPDATE",
    name="catering.event_requirement.update",
    description="Update Catering event requirements.",
    module="CATERING",
    resource="event_requirement",
    action="update",
)

CATERING_EVENT_REQUIREMENT_DELETE = Permission(
    code="CATERING.EVENT_REQUIREMENT.DELETE",
    name="catering.event_requirement.delete",
    description="Delete Catering event requirements.",
    module="CATERING",
    resource="event_requirement",
    action="delete",
)

CATERING_EVENT_REQUIREMENT_IDENTIFY = Permission(
    code="CATERING.EVENT_REQUIREMENT.IDENTIFY",
    name="catering.event_requirement.identify",
    description="Identify Catering event requirements.",
    module="CATERING",
    resource="event_requirement",
    action="identify",
)

CATERING_EVENT_REQUIREMENT_READY = Permission(
    code="CATERING.EVENT_REQUIREMENT.READY",
    name="catering.event_requirement.ready",
    description="Mark Catering event requirements ready.",
    module="CATERING",
    resource="event_requirement",
    action="ready",
)

CATERING_EVENT_REQUIREMENT_CANCEL = Permission(
    code="CATERING.EVENT_REQUIREMENT.CANCEL",
    name="catering.event_requirement.cancel",
    description="Cancel Catering event requirements.",
    module="CATERING",
    resource="event_requirement",
    action="cancel",
)

CATERING_PURCHASE_REQUIREMENT_SUBMIT_TO_PROCUREMENT = Permission(
    code="CATERING.CATERING_PURCHASE_REQUIREMENT.SUBMIT_TO_PROCUREMENT",
    name="catering.catering_purchase_requirement.submit_to_procurement",
    description="Submit Catering purchase requirements to Procurement.",
    module="CATERING",
    resource="catering_purchase_requirement",
    action="submit_to_procurement",
)


# ---------------------------------------------------------------------------
# Catering Quotation Permissions
# ---------------------------------------------------------------------------

CATERING_QUOTATION_CREATE = Permission(
    code="CATERING.CATERING_QUOTATION.CREATE",
    name="catering.catering_quotation.create",
    description="Create Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="create",
)

CATERING_QUOTATION_READ = Permission(
    code="CATERING.CATERING_QUOTATION.READ",
    name="catering.catering_quotation.read",
    description="Read Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="read",
)

CATERING_QUOTATION_UPDATE = Permission(
    code="CATERING.CATERING_QUOTATION.UPDATE",
    name="catering.catering_quotation.update",
    description="Update Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="update",
)

CATERING_QUOTATION_DELETE = Permission(
    code="CATERING.CATERING_QUOTATION.DELETE",
    name="catering.catering_quotation.delete",
    description="Delete Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="delete",
)

CATERING_QUOTATION_ISSUE = Permission(
    code="CATERING.CATERING_QUOTATION.ISSUE",
    name="catering.catering_quotation.issue",
    description="Issue Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="issue",
)

CATERING_QUOTATION_ACCEPT = Permission(
    code="CATERING.CATERING_QUOTATION.ACCEPT",
    name="catering.catering_quotation.accept",
    description="Accept Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="accept",
)

CATERING_QUOTATION_DECLINE = Permission(
    code="CATERING.CATERING_QUOTATION.DECLINE",
    name="catering.catering_quotation.decline",
    description="Decline Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="decline",
)

CATERING_QUOTATION_EXPIRE = Permission(
    code="CATERING.CATERING_QUOTATION.EXPIRE",
    name="catering.catering_quotation.expire",
    description="Expire Catering quotations.",
    module="CATERING",
    resource="catering_quotation",
    action="expire",
)


# ---------------------------------------------------------------------------
# Catering Revenue Permissions
# ---------------------------------------------------------------------------

CATERING_REVENUE_CREATE = Permission(
    code="CATERING.CATERING_REVENUE.CREATE",
    name="catering.catering_revenue.create",
    description="Create Catering revenue records.",
    module="CATERING",
    resource="catering_revenue",
    action="create",
)

CATERING_REVENUE_READ = Permission(
    code="CATERING.CATERING_REVENUE.READ",
    name="catering.catering_revenue.read",
    description="Read Catering revenue records.",
    module="CATERING",
    resource="catering_revenue",
    action="read",
)

CATERING_REVENUE_UPDATE = Permission(
    code="CATERING.CATERING_REVENUE.UPDATE",
    name="catering.catering_revenue.update",
    description="Update Catering revenue records.",
    module="CATERING",
    resource="catering_revenue",
    action="update",
)

CATERING_REVENUE_DELETE = Permission(
    code="CATERING.CATERING_REVENUE.DELETE",
    name="catering.catering_revenue.delete",
    description="Delete Catering revenue records.",
    module="CATERING",
    resource="catering_revenue",
    action="delete",
)

CATERING_REVENUE_ESTABLISH_ELIGIBILITY = Permission(
    code="CATERING.CATERING_REVENUE.ESTABLISH_ELIGIBILITY",
    name="catering.catering_revenue.establish_eligibility",
    description="Establish Catering revenue eligibility.",
    module="CATERING",
    resource="catering_revenue",
    action="establish_eligibility",
)

CATERING_REVENUE_RECOGNIZE = Permission(
    code="CATERING.CATERING_REVENUE.RECOGNIZE",
    name="catering.catering_revenue.recognize",
    description="Recognize Catering revenue.",
    module="CATERING",
    resource="catering_revenue",
    action="recognize",
)

CATERING_REVENUE_CANCEL = Permission(
    code="CATERING.CATERING_REVENUE.CANCEL",
    name="catering.catering_revenue.cancel",
    description="Cancel Catering revenue.",
    module="CATERING",
    resource="catering_revenue",
    action="cancel",
)


# ---------------------------------------------------------------------------
# Catering Expense Cost Association Permissions
# ---------------------------------------------------------------------------

CATERING_EXPENSE_COST_ASSOCIATION_CREATE = Permission(
    code="CATERING.EXPENSE_COST_ASSOCIATION.CREATE",
    name="catering.expense_cost_association.create",
    description="Create Catering Expense Cost Associations.",
    module="CATERING",
    resource="expense_cost_association",
    action="create",
)


# ---------------------------------------------------------------------------
# Aggregate Catering Permissions
# ---------------------------------------------------------------------------

CATERING_PERMISSIONS = (
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
    CATERING_PRODUCT_CATEGORY_UPDATE,
    CATERING_PRODUCT_CATEGORY_DELETE,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
    CATERING_PRODUCT_UPDATE,
    CATERING_PRODUCT_DELETE,
    CATERING_STOCK_ITEM_CREATE,
    CATERING_STOCK_ITEM_READ,
    CATERING_STOCK_ITEM_UPDATE,
    CATERING_STOCK_ITEM_DELETE,
    CATERING_INVENTORY_LOCATION_CREATE,
    CATERING_INVENTORY_LOCATION_READ,
    CATERING_INVENTORY_LOCATION_UPDATE,
    CATERING_INVENTORY_LOCATION_DELETE,
    CATERING_STOCK_BALANCE_READ,
    CATERING_STOCK_MOVEMENT_CREATE,
    CATERING_STOCK_MOVEMENT_READ,
    CATERING_STOCK_MOVEMENT_POST,
    CATERING_STOCK_TRANSFER_CREATE,
    CATERING_STOCK_TRANSFER_READ,
    CATERING_STOCK_TRANSFER_POST,
    CATERING_CUSTOMER_CREATE,
    CATERING_CUSTOMER_READ,
    CATERING_CUSTOMER_UPDATE,
    CATERING_CUSTOMER_DELETE,
    CATERING_REQUEST_CREATE,
    CATERING_REQUEST_READ,
    CATERING_REQUEST_UPDATE,
    CATERING_REQUEST_DELETE,
    CATERING_REQUEST_SUBMIT,
    CATERING_REQUEST_CANCEL,
    CATERING_EVENT_CREATE,
    CATERING_EVENT_READ,
    CATERING_EVENT_UPDATE,
    CATERING_EVENT_DELETE,
    CATERING_EVENT_QUOTE,
    CATERING_EVENT_CONFIRM,
    CATERING_EVENT_PLAN,
    CATERING_EVENT_READY,
    CATERING_EVENT_START_PRODUCTION,
    CATERING_EVENT_DELIVER,
    CATERING_EVENT_COMPLETE,
    CATERING_EVENT_CANCEL,
    CATERING_QUOTATION_CREATE,
    CATERING_QUOTATION_READ,
    CATERING_QUOTATION_UPDATE,
    CATERING_QUOTATION_DELETE,
    CATERING_QUOTATION_ISSUE,
    CATERING_QUOTATION_ACCEPT,
    CATERING_QUOTATION_DECLINE,
    CATERING_QUOTATION_EXPIRE,
    CATERING_REVENUE_CREATE,
    CATERING_REVENUE_READ,
    CATERING_REVENUE_UPDATE,
    CATERING_REVENUE_DELETE,
    CATERING_REVENUE_ESTABLISH_ELIGIBILITY,
    CATERING_REVENUE_RECOGNIZE,
    CATERING_REVENUE_CANCEL,
    CATERING_EVENT_REQUIREMENT_CREATE,
    CATERING_EVENT_REQUIREMENT_READ,
    CATERING_EVENT_REQUIREMENT_UPDATE,
    CATERING_EVENT_REQUIREMENT_DELETE,
    CATERING_EVENT_REQUIREMENT_IDENTIFY,
    CATERING_EVENT_REQUIREMENT_READY,
    CATERING_EVENT_REQUIREMENT_CANCEL,
    CATERING_PURCHASE_REQUIREMENT_SUBMIT_TO_PROCUREMENT,
    CATERING_EXPENSE_COST_ASSOCIATION_CREATE,
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
    "CATERING_STOCK_ITEM_CREATE",
    "CATERING_STOCK_ITEM_READ",
    "CATERING_STOCK_ITEM_UPDATE",
    "CATERING_STOCK_ITEM_DELETE",
    "CATERING_INVENTORY_LOCATION_CREATE",
    "CATERING_INVENTORY_LOCATION_READ",
    "CATERING_INVENTORY_LOCATION_UPDATE",
    "CATERING_INVENTORY_LOCATION_DELETE",
    "CATERING_STOCK_BALANCE_READ",
    "CATERING_STOCK_MOVEMENT_CREATE",
    "CATERING_STOCK_MOVEMENT_READ",
    "CATERING_STOCK_MOVEMENT_POST",
    "CATERING_STOCK_TRANSFER_CREATE",
    "CATERING_STOCK_TRANSFER_READ",
    "CATERING_STOCK_TRANSFER_POST",
    "CATERING_CUSTOMER_CREATE",
    "CATERING_CUSTOMER_READ",
    "CATERING_CUSTOMER_UPDATE",
    "CATERING_CUSTOMER_DELETE",
    "CATERING_REQUEST_CREATE",
    "CATERING_REQUEST_READ",
    "CATERING_REQUEST_UPDATE",
    "CATERING_REQUEST_DELETE",
    "CATERING_REQUEST_SUBMIT",
    "CATERING_REQUEST_CANCEL",
    "CATERING_EVENT_CREATE",
    "CATERING_EVENT_READ",
    "CATERING_EVENT_UPDATE",
    "CATERING_EVENT_DELETE",
    "CATERING_EVENT_QUOTE",
    "CATERING_EVENT_CONFIRM",
    "CATERING_EVENT_PLAN",
    "CATERING_EVENT_READY",
    "CATERING_EVENT_START_PRODUCTION",
    "CATERING_EVENT_DELIVER",
    "CATERING_EVENT_COMPLETE",
    "CATERING_EVENT_CANCEL",
    "CATERING_QUOTATION_CREATE",
    "CATERING_QUOTATION_READ",
    "CATERING_QUOTATION_UPDATE",
    "CATERING_QUOTATION_DELETE",
    "CATERING_QUOTATION_ISSUE",
    "CATERING_QUOTATION_ACCEPT",
    "CATERING_QUOTATION_DECLINE",
    "CATERING_QUOTATION_EXPIRE",
    "CATERING_REVENUE_CREATE",
    "CATERING_REVENUE_READ",
    "CATERING_REVENUE_UPDATE",
    "CATERING_REVENUE_DELETE",
    "CATERING_REVENUE_ESTABLISH_ELIGIBILITY",
    "CATERING_REVENUE_RECOGNIZE",
    "CATERING_REVENUE_CANCEL",
    "CATERING_EVENT_REQUIREMENT_CREATE",
    "CATERING_EVENT_REQUIREMENT_READ",
    "CATERING_EVENT_REQUIREMENT_UPDATE",
    "CATERING_EVENT_REQUIREMENT_DELETE",
    "CATERING_EVENT_REQUIREMENT_IDENTIFY",
    "CATERING_EVENT_REQUIREMENT_READY",
    "CATERING_EVENT_REQUIREMENT_CANCEL",
    "CATERING_PURCHASE_REQUIREMENT_SUBMIT_TO_PROCUREMENT",
    "CATERING_EXPENSE_COST_ASSOCIATION_CREATE",
    "CATERING_PERMISSIONS",
]
