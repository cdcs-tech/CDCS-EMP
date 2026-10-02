"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Finance Revenue workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class FinanceRevenueWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Finance Revenue.

    The workflow represents the Finance-owned lifecycle of a
    financial revenue record. It does not represent originating
    business recognition or integration delivery state.
    """

    PENDING = "PENDING"
    POSTED = "POSTED"

    ACTION_POST = "POST"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.PENDING,
                description=(
                    "Finance Revenue exists as a Finance-owned "
                    "financial representation that has not yet "
                    "been posted."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.POSTED,
                description=(
                    "Finance Revenue has been posted as the "
                    "completed Finance-side financial representation."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.PENDING,
                target=self.POSTED,
                action=self.ACTION_POST,
                metadata={
                    "operation": "finance_revenue.post",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "FinanceRevenueWorkflow",
]
