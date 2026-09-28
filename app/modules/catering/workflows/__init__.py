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

from app.modules.catering.workflows.movement import (
    StockMovementWorkflow,
)

from app.modules.catering.workflows.transfer import (
    StockTransferWorkflow,
)


__all__ = [
    "CateringRequestWorkflow",
    "CateringEventWorkflow",
    "StockMovementWorkflow",
    "StockTransferWorkflow",
]
