"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Event Requirement workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class EventRequirementWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Catering Event Requirements.

    An Event Requirement begins as a draft, becomes identified once
    its operational fulfilment classification has been established,
    and becomes ready when it is prepared for the appropriate
    fulfilment boundary.

    Inventory fulfilment and Procurement handoff are intentionally
    outside this workflow. This workflow owns only the Catering-side
    Event Requirement lifecycle.
    """

    DRAFT = "DRAFT"
    IDENTIFIED = "IDENTIFIED"
    READY = "READY"
    CANCELLED = "CANCELLED"

    ACTION_IDENTIFY = "IDENTIFY"
    ACTION_READY = "READY"
    ACTION_CANCEL = "CANCEL"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.DRAFT,
                description=(
                    "Event Requirement has been created but "
                    "has not yet been fully identified and "
                    "classified for fulfilment."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.IDENTIFIED,
                description=(
                    "Event Requirement has been identified and "
                    "has an explicit fulfilment classification."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.READY,
                description=(
                    "Event Requirement has passed Catering-side "
                    "planning validation and is ready for the "
                    "appropriate fulfilment path."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.CANCELLED,
                description=(
                    "Event Requirement has been cancelled "
                    "and is no longer active."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.IDENTIFIED,
                action=self.ACTION_IDENTIFY,
                metadata={
                    "operation": "catering_event_requirement.identify",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.IDENTIFIED,
                target=self.READY,
                action=self.ACTION_READY,
                metadata={
                    "operation": "catering_event_requirement.ready",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DRAFT,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_event_requirement.cancel",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.IDENTIFIED,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_event_requirement.cancel",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "EventRequirementWorkflow",
]
