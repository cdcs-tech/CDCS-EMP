"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Request workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class CateringRequestWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Catering Requests.

    Requests begin as DRAFT, may be submitted for processing,
    and may be cancelled before becoming a confirmed Catering Event.

    Request-to-Event creation and quotation confirmation are
    intentionally outside this workflow until the corresponding
    B3/B4 business contracts are implemented.
    """

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"

    ACTION_SUBMIT = "SUBMIT"
    ACTION_CANCEL = "CANCEL"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Catering Request has been created but "
                    "has not yet been submitted."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.SUBMITTED,
                description=(
                    "Catering Request has been submitted "
                    "for processing."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.CANCELLED,
                description=(
                    "Catering Request has been cancelled "
                    "and is no longer active."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.SUBMITTED,
                action=self.ACTION_SUBMIT,
                metadata={
                    "operation": "catering_request.submit",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_request.cancel",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.SUBMITTED,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_request.cancel",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "CateringRequestWorkflow",
]
