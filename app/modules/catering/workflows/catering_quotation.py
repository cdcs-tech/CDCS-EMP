"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Quotation workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class CateringQuotationWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Catering Quotations.

    A quotation begins as a draft, may be issued to the customer,
    and then reaches one of the terminal commercial outcomes:
    accepted, declined, or expired.

    Quotation acceptance is a Catering/customer commercial decision.
    It does not itself mutate the associated Catering Event lifecycle.
    """

    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"

    ACTION_ISSUE = "ISSUE"
    ACTION_ACCEPT = "ACCEPT"
    ACTION_DECLINE = "DECLINE"
    ACTION_EXPIRE = "EXPIRE"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Catering Quotation has been created but "
                    "has not yet been issued to the customer."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.ISSUED,
                description=(
                    "Catering Quotation has been issued to the "
                    "customer and is awaiting a commercial outcome."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.ACCEPTED,
                description=(
                    "Catering Quotation has been accepted by the "
                    "customer."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.DECLINED,
                description=(
                    "Catering Quotation has been declined by the "
                    "customer."
                )
            )
        )

        self.add_state(
            WorkflowState(
                name=self.EXPIRED,
                description=(
                    "Catering Quotation has passed its validity "
                    "period without being accepted."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.ISSUED,
                action=self.ACTION_ISSUE,
                metadata={
                    "operation": "catering_quotation.issue",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.ISSUED,
                target=self.ACCEPTED,
                action=self.ACTION_ACCEPT,
                metadata={
                    "operation": "catering_quotation.accept",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.ISSUED,
                target=self.DECLINED,
                action=self.ACTION_DECLINE,
                metadata={
                    "operation": "catering_quotation.decline",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.ISSUED,
                target=self.EXPIRED,
                action=self.ACTION_EXPIRE,
                metadata={
                    "operation": "catering_quotation.expire",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "CateringQuotationWorkflow",
]
