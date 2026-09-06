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
    "CATERING_PERMISSIONS",
]
