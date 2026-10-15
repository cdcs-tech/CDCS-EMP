"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Forms public API.
"""

from app.modules.catering.forms.product import (
    ProductForm,
)
from app.modules.catering.forms.product_category import (
    ProductCategoryForm,
)

from app.modules.catering.forms.stock_item import (
    StockItemForm,
)

from app.modules.catering.forms.location import InventoryLocationForm

from app.modules.catering.forms.movement import (
    StockMovementForm,
)

from app.modules.catering.forms.transfer import (
    StockTransferForm,
)

from .customer import CustomerForm

from .catering_request import CateringRequestForm

from app.modules.catering.forms.catering_event import CateringEventForm

from app.modules.catering.forms.catering_revenue import CateringRevenueForm

from app.modules.catering.forms.catering_quotation import (
    CateringQuotationForm,
    CateringQuotationLineForm,
)

from app.modules.catering.forms.event_requirement import (
    EventRequirementForm,
    FULFILMENT_TYPE_CHOICES,
)

from app.modules.catering.forms.catering_purchase_requirement import (
    CateringPurchaseRequirementForm,
)

from app.modules.catering.forms.expense_cost_association import (
    CateringExpenseCostAssociationForm,
)

__all__ = [
    "ProductForm",
    "ProductCategoryForm",
    "StockItemForm",
    "InventoryLocationForm",
    "StockMovementForm",
    "StockTransferForm",
    "CustomerForm",
    "CateringRequestForm",
    "CateringEventForm",
    "CateringRevenueForm",
    "CateringQuotationForm",
    "CateringQuotationLineForm",
    "EventRequirementForm",
    "CateringPurchaseRequirementForm",
    "FULFILMENT_TYPE_CHOICES",
    "CateringExpenseCostAssociationForm",
]
