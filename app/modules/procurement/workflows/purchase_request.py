"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Workflows

Purchase Request workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class PurchaseRequestWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Procurement Purchase Requests.

    Purchase Requests progress through a controlled approval
    lifecycle. A submitted request may be approved, rejected,
    or returned to draft for controlled correction.
    """

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

    ACTION_SUBMIT = "SUBMIT"
    ACTION_APPROVE = "APPROVE"
    ACTION_REJECT = "REJECT"
    ACTION_RETURN = "RETURN"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Purchase Request is being prepared "
                    "and may be edited."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.SUBMITTED,
                description=(
                    "Purchase Request has been submitted "
                    "for approval."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.APPROVED,
                description=(
                    "Purchase Request has been approved."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.REJECTED,
                description=(
                    "Purchase Request has been rejected "
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
                    "operation": "purchase_request.submit",
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
                    "operation": "purchase_request.approve",
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
                    "operation": "purchase_request.reject",
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
                    "operation": "purchase_request.return",
                    "terminal": False,
                },
            )
        )


__all__ = [
    "PurchaseRequestWorkflow",
]
