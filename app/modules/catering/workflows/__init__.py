"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory Workflows

Public workflow definitions for Catering Inventory.
"""

from app.modules.catering.workflows.movement import (
    StockMovementWorkflow,
)

from app.modules.catering.workflows.transfer import (
    StockTransferWorkflow,
)


__all__ = [
    "StockMovementWorkflow",
    "StockTransferWorkflow",
]
