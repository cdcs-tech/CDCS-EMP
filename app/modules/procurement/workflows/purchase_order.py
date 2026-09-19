"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Workflows

Purchase Order workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class PurchaseOrderWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Procurement Purchase Orders.

    Purchase Orders progress through a controlled
    supplier-facing procurement commitment lifecycle.
    A submitted order may be approved, rejected, or
    returned to draft for controlled correction.
    An approved order may be cancelled.
    """

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

    ACTION_SUBMIT = "SUBMIT"
    ACTION_APPROVE = "APPROVE"
    ACTION_REJECT = "REJECT"
    ACTION_RETURN = "RETURN"
    ACTION_CANCEL = "CANCEL"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Purchase Order is being prepared "
                    "and may be edited."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.SUBMITTED,
                description=(
                    "Purchase Order has been submitted "
                    "for approval."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.APPROVED,
                description=(
                    "Purchase Order has been approved "
                    "and represents an authorized "
                    "procurement commitment."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.REJECTED,
                description=(
                    "Purchase Order has been rejected "
                    "and is terminal."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.CANCELLED,
                description=(
                    "Purchase Order has been cancelled "
                    "and is terminal."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.SUBMITTED,
                action=self.ACTION_SUBMIT,
                metadata={
                    "operation": "purchase_order.submit",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.SUBMITTED,
                target=self.APPROVED,
                action=self.ACTION_APPROVE,
                metadata={
                    "operation": "purchase_order.approve",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.SUBMITTED,
                target=self.REJECTED,
                action=self.ACTION_REJECT,
                metadata={
                    "operation": "purchase_order.reject",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.SUBMITTED,
                target=self.DRAFT,
                action=self.ACTION_RETURN,
                metadata={
                    "operation": "purchase_order.return",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.APPROVED,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "purchase_order.cancel",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "PurchaseOrderWorkflow",
]
