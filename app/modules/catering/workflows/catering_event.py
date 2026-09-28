"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event workflow definition.
"""

from app.core.workflow import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


class CateringEventWorkflow(BaseWorkflow):
    """
    Enterprise workflow for Catering Events.

    The lifecycle follows the approved B1 Catering domain
    workflow. Quotation acceptance and Request-to-Event
    creation are business boundaries outside this workflow.
    """

    REQUESTED = "REQUESTED"
    QUOTED = "QUOTED"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    PLANNING = "PLANNING"
    READY = "READY"
    IN_PRODUCTION = "IN_PRODUCTION"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    ACTION_QUOTE = "QUOTE"
    ACTION_CONFIRM = "CONFIRM"
    ACTION_PLAN = "PLAN"
    ACTION_READY = "READY"
    ACTION_START_PRODUCTION = "START_PRODUCTION"
    ACTION_DELIVER = "DELIVER"
    ACTION_COMPLETE = "COMPLETE"
    ACTION_CANCEL = "CANCEL"

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=self.REQUESTED,
                description=(
                    "Catering Event has been created from an "
                    "accepted or confirmed business engagement "
                    "and is awaiting quotation processing."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.QUOTED,
                description=(
                    "Catering Event has an associated quotation "
                    "and is awaiting confirmation."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.PENDING_CONFIRMATION,
                description=(
                    "Catering Event is awaiting customer "
                    "confirmation."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.CONFIRMED,
                description=(
                    "Catering Event has been confirmed and "
                    "may proceed to operational planning."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.PLANNING,
                description=(
                    "Catering Event is undergoing operational "
                    "planning."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.READY,
                description=(
                    "Catering Event is operationally ready "
                    "for production."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.IN_PRODUCTION,
                description=(
                    "Catering Event is currently being "
                    "prepared or produced."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.DELIVERED,
                description=(
                    "Catering Event service has been delivered."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.COMPLETED,
                description=(
                    "Catering Event has completed its "
                    "operational lifecycle."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=self.CANCELLED,
                description=(
                    "Catering Event has been cancelled "
                    "and is no longer active."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.REQUESTED,
                target=self.QUOTED,
                action=self.ACTION_QUOTE,
                metadata={
                    "operation": "catering_event.quote",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.QUOTED,
                target=self.PENDING_CONFIRMATION,
                action=self.ACTION_CONFIRM,
                metadata={
                    "operation": "catering_event.request_confirmation",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.PENDING_CONFIRMATION,
                target=self.CONFIRMED,
                action=self.ACTION_CONFIRM,
                metadata={
                    "operation": "catering_event.confirm",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.CONFIRMED,
                target=self.PLANNING,
                action=self.ACTION_PLAN,
                metadata={
                    "operation": "catering_event.plan",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.PLANNING,
                target=self.READY,
                action=self.ACTION_READY,
                metadata={
                    "operation": "catering_event.ready",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.READY,
                target=self.IN_PRODUCTION,
                action=self.ACTION_START_PRODUCTION,
                metadata={
                    "operation": "catering_event.start_production",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.IN_PRODUCTION,
                target=self.DELIVERED,
                action=self.ACTION_DELIVER,
                metadata={
                    "operation": "catering_event.deliver",
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.DELIVERED,
                target=self.COMPLETED,
                action=self.ACTION_COMPLETE,
                metadata={
                    "operation": "catering_event.complete",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.REQUESTED,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_event.cancel",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.QUOTED,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_event.cancel",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=self.PENDING_CONFIRMATION,
                target=self.CANCELLED,
                action=self.ACTION_CANCEL,
                metadata={
                    "operation": "catering_event.cancel",
                    "terminal": True,
                },
            )
        )


__all__ = [
    "CateringEventWorkflow",
]
