"""
CDCS-EMP Event Governance End-to-End Test
"""

from app.core.events import (
    BaseEvent,
    EventPublisher,
)

from app.core.events.audit_handler import (
    EventAuditHandler,
)

from app.core.events.workflow_handler import (
    EventWorkflowHandler,
)

from app.core.events.registry import (
    event_registry,
)

from app.core.security.audit_registry import (
    audit_registry,
)

from app.core.workflow.base import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)

from app.core.workflow.registry import (
    WorkflowDefinition,
    workflow_registry,
)



class EmployeeApprovedWorkflow(
    BaseWorkflow
):

    def __init__(self):

        super().__init__()

        self.add_state(
            WorkflowState(
                "PENDING"
            )
        )

        self.add_state(
            WorkflowState(
                "APPROVED"
            )
        )

        self.add_transition(
            WorkflowTransition(
                source="PENDING",
                target="APPROVED",
                action="APPROVE",
            )
        )



class EmployeeApprovedEvent(
    BaseEvent
):

    @property
    def event_name(self):

        return (
            "employee.approved"
        )


    def metadata(self):

        data = super().metadata()

        data.update(
            {
                "workflow_module": "hr",
                "workflow_name": (
                    "employee_approval"
                ),
                "workflow_source": (
                    "PENDING"
                ),
                "workflow_target": (
                    "APPROVED"
                ),
            }
        )

        return data



def test_complete_event_governance_flow():

    audit_registry.clear()

    workflow_registry.clear()

    event_registry.clear()


    workflow_registry.register(
        WorkflowDefinition(
            module_name="hr",
            workflow_name=(
                "employee_approval"
            ),
            workflow=(
                EmployeeApprovedWorkflow()
            ),
        )
    )


    event = (
        EmployeeApprovedEvent()
    )


    publisher = (
        EventPublisher()
    )


    # publish validation pipeline
    publisher.publish(
        event
    )


    # audit integration
    audit_handler = (
        EventAuditHandler()
    )

    audit_handler.handle(
        event
    )


    assert (
        audit_registry.count()
        == 1
    )


    audit = (
        audit_registry.latest()
    )


    assert (
        audit.event_type
        ==
        "employee.approved"
    )


    # workflow integration
    workflow_handler = (
        EventWorkflowHandler()
    )


    result = (
        workflow_handler.handle(
            event
        )
    )


    assert (
        result.name
        ==
        "APPROVED"
    )


    audit_registry.clear()

    workflow_registry.clear()

    event_registry.clear()

