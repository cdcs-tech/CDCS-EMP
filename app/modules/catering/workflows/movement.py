"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory Workflows

Stock movement workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class StockMovementWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Catering stock movements.

    Stock movements may be created in DRAFT status and
    transitioned to POSTED status. A POSTED movement is
    terminal and immutable at the business-service layer.
    """

    DRAFT = "DRAFT"
    POSTED = "POSTED"

    ACTION_POST = "POST"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Stock movement has been created but "
                    "has not yet affected inventory."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.POSTED,
                description=(
                    "Stock movement has been posted and "
                    "has affected inventory."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.POSTED,
                action=self.ACTION_POST,
                metadata={
                    "operation": "stock_movement.post",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "StockMovementWorkflow",
]
