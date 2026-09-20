"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration

Public integration contract API.
"""

from app.modules.procurement.integration.contracts import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)

__all__ = [
    "INVENTORY_INTEGRATION_PROVIDER",
    "INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION",
    "PurchaseOrderReceiptRequest",
]
