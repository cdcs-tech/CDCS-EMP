"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Workflow Framework

Base workflow engine.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class WorkflowState:
    """
    Represents a workflow state.
    """

    name: str

    description: str = ""


@dataclass(slots=True, frozen=True)
class WorkflowTransition:
    """
    Represents a valid workflow transition.
    """

    source: str

    target: str

    action: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


class BaseWorkflow(ABC):
    """
    Base workflow implementation.
    """

    def __init__(self):
        self._states: dict[str, WorkflowState] = {}
        self._transitions: list[
            WorkflowTransition
        ] = []


    def add_state(
        self,
        state: WorkflowState,
    ) -> None:
        """
        Register a workflow state.
        """

        self._states[state.name] = state


    def add_transition(
        self,
        transition: WorkflowTransition,
    ) -> None:
        """
        Register a workflow transition.
        """

        self._transitions.append(
            transition
        )


    def get_state(
        self,
        name: str,
    ) -> WorkflowState | None:
        """
        Return a workflow state.
        """

        return self._states.get(name)


    def states(self) -> list[WorkflowState]:
        """
        Return all workflow states.
        """

        return list(
            self._states.values()
        )


    def transitions(self) -> list[
        WorkflowTransition
    ]:
        """
        Return all workflow transitions.
        """

        return list(
            self._transitions
        )


    def can_transition(
        self,
        source: str,
        target: str,
    ) -> bool:
        """
        Determine whether a transition is allowed.
        """

        return any(
            transition.source == source
            and transition.target == target
            for transition in self._transitions
        )


    def transition(
        self,
        source: str,
        target: str,
    ) -> WorkflowState:
        """
        Execute a workflow transition.
        """

        if not self.can_transition(
            source,
            target,
        ):
            raise ValueError(
                f"Invalid workflow transition: "
                f"{source} -> {target}"
            )

        state = self.get_state(target)

        if state is None:
            raise ValueError(
                f"Workflow state "
                f"'{target}' does not exist."
            )

        return state
