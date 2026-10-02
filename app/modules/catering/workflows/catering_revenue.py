"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Revenue workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class CateringRevenueWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Catering Revenue.

    Revenue recognition is an explicit Catering business decision.
    The workflow does not infer eligibility or recognition from
    Catering Event lifecycle status.
    """

    DRAFT = "DRAFT"
    ELIGIBLE = "ELIGIBLE"
    RECOGNIZED = "RECOGNIZED"
    CANCELLED = "CANCELLED"

    ACTION_ESTABLISH_ELIGIBILITY = "ESTABLISH_ELIGIBILITY"
    ACTION_RECOGNIZE = "RECOGNIZE"
    ACTION_CANCEL = "CANCEL"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Catering Revenue has been created but has not "
                    "yet passed the explicit eligibility boundary."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.ELIGIBLE,
                description=(
                    "Catering Revenue has passed the explicit Catering "
                    "eligibility boundary and may be recognized."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.RECOGNIZED,
                description=(
                    "Catering Revenue has been established as an "
                    "authoritative Catering revenue fact."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.CANCELLED,
                description=(
                    "Catering Revenue has been explicitly cancelled."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.ELIGIBLE,
                action=self.ACTION_ESTABLISH_ELIGIBILITY,
                metadata={
                    "operation": (
                        "catering_revenue.establish_eligibility"
                    ),
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.ELIGIBLE,
                target=self.RECOGNIZED,
                action=self.ACTION_RECOGNIZE,
                metadata={
                    "operation": "catering_revenue.recognize",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_revenue.cancel",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.ELIGIBLE,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_revenue.cancel",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "CateringRevenueWorkflow",
]
