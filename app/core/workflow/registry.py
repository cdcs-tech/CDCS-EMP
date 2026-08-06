"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Workflow Framework

Workflow registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from app.core.workflow.base import BaseWorkflow


@dataclass(slots=True)
class WorkflowDefinition:
    """
    Defines a registered workflow.
    """

    module_name: str

    workflow_name: str

    workflow: BaseWorkflow


class WorkflowRegistry:
    """
    Registry for enterprise workflows.
    """

    def __init__(self):
        self._workflows: dict[
            tuple[str, str],
            WorkflowDefinition,
        ] = {}


    def register(
        self,
        definition: WorkflowDefinition,
    ) -> None:
        """
        Register a workflow definition.
        """

        key = (
            definition.module_name,
            definition.workflow_name,
        )

        self._workflows[key] = definition


    def get(
        self,
        module_name: str,
        workflow_name: str,
    ) -> WorkflowDefinition | None:
        """
        Return a workflow definition.
        """

        return self._workflows.get(
            (
                module_name,
                workflow_name,
            )
        )


    def has(
        self,
        module_name: str,
        workflow_name: str,
    ) -> bool:
        """
        Determine whether a workflow exists.
        """

        return (
            (
                module_name,
                workflow_name,
            )
            in self._workflows
        )


    def all(
        self,
    ) -> list[WorkflowDefinition]:
        """
        Return all registered workflows.
        """

        return list(
            self._workflows.values()
        )


    def clear(self) -> None:
        """
        Remove all workflow registrations.
        """

        self._workflows.clear()


    def count(self) -> int:
        """
        Return the number of registered workflows.
        """

        return len(self._workflows)


    def __iter__(
        self,
    ) -> Iterator[WorkflowDefinition]:
        """
        Iterate over registered workflows.
        """

        return iter(
            self._workflows.values()
        )


workflow_registry = WorkflowRegistry()
