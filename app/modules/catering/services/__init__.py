"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Services

Module-local application services.
"""

from .balance import StockBalanceService
from .catering_event import CateringEventService
from .catering_quotation import CateringQuotationService
from .catering_quotation_event_coordination import (
    CateringQuotationEventCoordinationService,
)
from .catering_request import CateringRequestService
from .location import InventoryLocationService
from .movement import StockMovementService
from .product import ProductService
from .product_category import ProductCategoryService
from .stock_item import StockItemService
from .transfer import StockTransferService
from .event_requirement import EventRequirementService
from .procurement_handoff import CateringProcurementHandoffService
from .customer import CustomerService
from .expense_cost_association import (
    CateringExpenseCostAssociationService,
)
from app.modules.catering.services.expense_cost_consumption import (
    CateringExpenseCostConsumptionService,
)
from app.modules.catering.services.catering_revenue import (
    CateringRevenueService,
)

__all__ = [
    "ProductService",
    "ProductCategoryService",
    "StockItemService",
    "InventoryLocationService",
    "StockBalanceService",
    "StockMovementService",
    "StockTransferService",
    "CateringEventService",
    "CateringRequestService",
    "CateringQuotationService",
    "CateringQuotationEventCoordinationService",
    "EventRequirementService",
    "CateringProcurementHandoffService",
    "CateringExpenseCostAssociationService",
    "CateringExpenseCostConsumptionService",
    "CateringRevenueService",
    "CustomerService",
]
