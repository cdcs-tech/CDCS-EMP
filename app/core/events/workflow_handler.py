"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Event Framework

Event Workflow Handler

Bridges enterprise events with
the Workflow Framework.
"""

from app.core.workflow.registry import (
    workflow_registry,
)


class EventWorkflowHandler:
    """
    Handles workflow transitions triggered
    by enterprise events.
    """


    def handle(
        self,
        event,
    ):
        """
        Process workflow triggers from events.

        Expected event metadata:

        workflow_module
        workflow_name
        workflow_source
        workflow_target
        """

        metadata = (
            event.metadata()
        )


        workflow_module = metadata.get(
            "workflow_module"
        )

        workflow_name = metadata.get(
            "workflow_name"
        )

        source_state = metadata.get(
            "workflow_source"
        )

        target_state = metadata.get(
            "workflow_target"
        )


        # No workflow trigger attached
        if not all(
            [
                workflow_module,
                workflow_name,
                source_state,
                target_state,
            ]
        ):

            return None


        definition = (
            workflow_registry.get(
                workflow_module,
                workflow_name,
            )
        )


        if definition is None:

            raise ValueError(
                "Workflow definition not found."
            )


        workflow = (
            definition.workflow
        )


        return workflow.transition(
            source_state,
            target_state,
        )


    def __repr__(self):

        return (
            "<EventWorkflowHandler>"
        )

