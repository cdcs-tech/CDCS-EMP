"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Handler exports.
"""

from app.modules.procurement.handlers.purchase_order import (
    ApprovePurchaseOrderHandler,
    CancelPurchaseOrderHandler,
    RejectPurchaseOrderHandler,
    ReturnPurchaseOrderHandler,
    SubmitPurchaseOrderHandler,
)
from app.modules.procurement.handlers.purchase_request import (
    ApprovePurchaseRequestHandler,
    RejectPurchaseRequestHandler,
    ReturnPurchaseRequestHandler,
    SubmitPurchaseRequestHandler,
)
from app.modules.procurement.handlers.purchase_order_receive import (
    ReceivePurchaseOrderHandler,
)

__all__ = [
    "ApprovePurchaseOrderHandler",
    "ApprovePurchaseRequestHandler",
    "CancelPurchaseOrderHandler",
    "RejectPurchaseOrderHandler",
    "RejectPurchaseRequestHandler",
    "ReturnPurchaseOrderHandler",
    "ReturnPurchaseRequestHandler",
    "SubmitPurchaseOrderHandler",
    "SubmitPurchaseRequestHandler",
    "ReceivePurchaseOrderHandler",
]
