"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Workflows

Public workflow definitions for Catering.
"""

from app.modules.catering.workflows.catering_event import (
    CateringEventWorkflow,
)

from app.modules.catering.workflows.catering_request import (
    CateringRequestWorkflow,
)

from app.modules.catering.workflows.catering_quotation import (
    CateringQuotationWorkflow,
)

from app.modules.catering.workflows.event_requirement import (
    EventRequirementWorkflow,
)

from app.modules.catering.workflows.movement import (
    StockMovementWorkflow,
)

from app.modules.catering.workflows.transfer import (
    StockTransferWorkflow,
)

from app.modules.catering.workflows.catering_revenue import (
    CateringRevenueWorkflow,
)


__all__ = [
    "CateringRequestWorkflow",
    "CateringEventWorkflow",
    "CateringQuotationWorkflow",
    "EventRequirementWorkflow",
    "StockMovementWorkflow",
    "StockTransferWorkflow",
    "CateringRevenueWorkflow",
]
