"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Repositories

Module-local persistence repositories.
"""

from .balance import StockBalanceRepository
from .catering_event import CateringEventRepository
from .catering_request import CateringRequestRepository
from .catering_quotation import CateringQuotationRepository
from .location import InventoryLocationRepository
from .movement import StockMovementRepository
from .product import ProductRepository
from .product_category import ProductCategoryRepository
from .stock_item import StockItemRepository
from .transfer import StockTransferRepository
from .event_requirement import EventRequirementRepository
from .catering_purchase_requirement import (
    CateringPurchaseRequirementRepository,
)
from .expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)
from .catering_revenue import (
    CateringRevenueRepository,
)

__all__ = [
    "ProductRepository",
    "ProductCategoryRepository",
    "StockItemRepository",
    "InventoryLocationRepository",
    "StockBalanceRepository",
    "StockMovementRepository",
    "StockTransferRepository",
    "CateringEventRepository",
    "CateringRequestRepository",
    "CateringQuotationRepository",
    "EventRequirementRepository",
    "CateringPurchaseRequirementRepository",
    "CateringExpenseCostAssociationRepository",
    "CateringRevenueRepository",
]
