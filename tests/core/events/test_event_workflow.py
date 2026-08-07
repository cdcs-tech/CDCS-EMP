"""
CDCS-EMP Event Workflow Integration Test
"""

from app.core.events import (
    BaseEvent,
    EventWorkflowHandler,
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


class TestWorkflow(BaseWorkflow):

    def __init__(self):

        super().__init__()

        self.add_state(
            WorkflowState("PENDING")
        )

        self.add_state(
            WorkflowState("APPROVED")
        )

        self.add_transition(
            WorkflowTransition(
                source="PENDING",
                target="APPROVED",
                action="APPROVE",
            )
        )



class WorkflowEvent(BaseEvent):

    @property
    def event_name(self):

        return "test.workflow.event"


    def metadata(self):

        data = super().metadata()

        data.update(
            {
                "workflow_module": "test",
                "workflow_name": "approval",
                "workflow_source": "PENDING",
                "workflow_target": "APPROVED",
            }
        )

        return data



def test_event_triggers_workflow():

    workflow_registry.clear()


    workflow_registry.register(
        WorkflowDefinition(
            module_name="test",
            workflow_name="approval",
            workflow=TestWorkflow(),
        )
    )


    handler = EventWorkflowHandler()

    event = WorkflowEvent()


    result = handler.handle(
        event
    )


    assert (
        result.name
        == "APPROVED"
    )


    workflow_registry.clear()

