"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution lifecycle contract.
"""

from __future__ import annotations

from enum import Enum

from app.core.execution.exceptions import (
    ExecutionContractException,
)


class ExecutionLifecycleState(str, Enum):
    """
    Standard enterprise execution lifecycle states.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"


class ExecutionLifecycle:
    """
    Manages the lifecycle state of a command execution.

    The lifecycle contract permits only explicitly defined
    state transitions and protects terminal states from
    further transitions.
    """

    _TRANSITIONS = {
        ExecutionLifecycleState.PENDING: {
            ExecutionLifecycleState.RUNNING,
        },
        ExecutionLifecycleState.RUNNING: {
            ExecutionLifecycleState.COMPLETED,
            ExecutionLifecycleState.FAILED,
            ExecutionLifecycleState.DENIED,
        },
        ExecutionLifecycleState.COMPLETED: set(),
        ExecutionLifecycleState.FAILED: set(),
        ExecutionLifecycleState.DENIED: set(),
    }

    def __init__(
        self,
        state: ExecutionLifecycleState = (
            ExecutionLifecycleState.PENDING
        ),
    ) -> None:
        """
        Initialize an execution lifecycle.
        """

        self._validate_state(state)

        self._state = state

    @property
    def state(self) -> ExecutionLifecycleState:
        """
        Return the current lifecycle state.
        """

        return self._state

    def can_transition(
        self,
        target: ExecutionLifecycleState,
    ) -> bool:
        """
        Determine whether a transition is permitted.
        """

        self._validate_state(target)

        return target in self._TRANSITIONS[
            self._state
        ]

    def transition(
        self,
        target: ExecutionLifecycleState,
    ) -> None:
        """
        Transition to a permitted lifecycle state.
        """

        self._validate_state(target)

        if not self.can_transition(target):
            raise ExecutionContractException(
                "Invalid execution lifecycle transition "
                f"from '{self._state.value}' to "
                f"'{target.value}'."
            )

        self._state = target

    def is_terminal(self) -> bool:
        """
        Determine whether the current state is terminal.
        """

        return self._state in {
            ExecutionLifecycleState.COMPLETED,
            ExecutionLifecycleState.FAILED,
            ExecutionLifecycleState.DENIED,
        }

    @staticmethod
    def _validate_state(
        state: ExecutionLifecycleState,
    ) -> None:
        """
        Validate a lifecycle state.
        """

        if not isinstance(
            state,
            ExecutionLifecycleState,
        ):
            raise ExecutionContractException(
                "Execution lifecycle state must be an "
                "ExecutionLifecycleState."
            )
