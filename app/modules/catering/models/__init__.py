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

from .catering_event import CateringEvent
from .catering_request import CateringRequest
from .customer import Customer
from .location import InventoryLocation
from .product import Product
from .product_category import ProductCategory
from .stock_balance import StockBalance
from .stock_item import StockItem
from .stock_movement import StockMovement
from .stock_transfer import StockTransfer
from app.modules.catering.models.catering_quotation import (
    CateringQuotation,
)
from app.modules.catering.models.catering_quotation_line import (
    CateringQuotationLine,
)
from .event_requirement import EventRequirement

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    "CateringEvent",
    "CateringRequest",
    "Customer",
    "ProductCategory",
    "Product",
    "StockItem",
    "InventoryLocation",
    "StockBalance",
    "StockMovement",
    "StockTransfer",
    "CateringQuotation",
    "CateringQuotationLine",
    "EventRequirement",
]
