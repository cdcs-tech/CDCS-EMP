"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution lifecycle governance contract.
"""

from __future__ import annotations

from enum import Enum

from app.core.execution.events import (
    ExecutionEventType,
)


class ExecutionGovernanceState(str, Enum):
    """
    Standard execution lifecycle governance states.
    """

    CREATED = "created"

    AUTHORIZED = "authorized"

    STARTED = "started"

    COMPLETED = "completed"

    FAILED = "failed"

    DENIED = "denied"


class ExecutionGovernanceDecision:
    """
    Represents the result of an execution lifecycle
    governance transition evaluation.
    """

    def __init__(
        self,
        *,
        allowed: bool,
        current_state: ExecutionGovernanceState,
        target_state: ExecutionGovernanceState,
        reason: str = "",
    ) -> None:
        self.allowed = allowed
        self.current_state = current_state
        self.target_state = target_state
        self.reason = reason

    def is_allowed(self) -> bool:
        """
        Determine whether the requested transition
        is allowed.
        """

        return self.allowed

    def is_denied(self) -> bool:
        """
        Determine whether the requested transition
        is denied.
        """

        return not self.allowed


class ExecutionGovernanceContract:
    """
    Governs execution lifecycle state transitions.

    This contract does not perform authorization,
    command execution, transaction management, or
    observability.

    It only guarantees that execution lifecycle
    transitions follow the enterprise execution
    state model.
    """

    _TRANSITIONS = {
        ExecutionGovernanceState.CREATED: {
            ExecutionGovernanceState.AUTHORIZED,
            ExecutionGovernanceState.DENIED,
        },
        ExecutionGovernanceState.AUTHORIZED: {
            ExecutionGovernanceState.STARTED,
            ExecutionGovernanceState.DENIED,
        },
        ExecutionGovernanceState.STARTED: {
            ExecutionGovernanceState.COMPLETED,
            ExecutionGovernanceState.FAILED,
        },
        ExecutionGovernanceState.COMPLETED: set(),
        ExecutionGovernanceState.FAILED: set(),
        ExecutionGovernanceState.DENIED: set(),
    }

    _EVENT_TO_STATE = {
        ExecutionEventType.STARTED:
            ExecutionGovernanceState.STARTED,

        ExecutionEventType.COMPLETED:
            ExecutionGovernanceState.COMPLETED,

        ExecutionEventType.FAILED:
            ExecutionGovernanceState.FAILED,

        ExecutionEventType.DENIED:
            ExecutionGovernanceState.DENIED,
    }

    def __init__(
        self,
        initial_state: ExecutionGovernanceState = (
            ExecutionGovernanceState.CREATED
        ),
    ) -> None:
        """
        Initialize execution lifecycle governance.
        """

        if not isinstance(
            initial_state,
            ExecutionGovernanceState,
        ):
            raise TypeError(
                "initial_state must be an "
                "ExecutionGovernanceState."
            )

        self._state = initial_state

    @property
    def state(self) -> ExecutionGovernanceState:
        """
        Return the current execution lifecycle state.
        """

        return self._state

    def can_transition(
        self,
        target_state: ExecutionGovernanceState,
    ) -> bool:
        """
        Determine whether a lifecycle transition
        is permitted.
        """

        if not isinstance(
            target_state,
            ExecutionGovernanceState,
        ):
            raise TypeError(
                "target_state must be an "
                "ExecutionGovernanceState."
            )

        return target_state in self._TRANSITIONS[
            self._state
        ]

    def evaluate(
        self,
        target_state: ExecutionGovernanceState,
    ) -> ExecutionGovernanceDecision:
        """
        Evaluate a requested lifecycle transition
        without changing the current state.
        """

        if not isinstance(
            target_state,
            ExecutionGovernanceState,
        ):
            raise TypeError(
                "target_state must be an "
                "ExecutionGovernanceState."
            )

        allowed = self.can_transition(
            target_state
        )

        if allowed:
            reason = "Execution lifecycle transition allowed."
        else:
            reason = (
                f"Invalid execution lifecycle transition "
                f"from '{self._state.value}' to "
                f"'{target_state.value}'."
            )

        return ExecutionGovernanceDecision(
            allowed=allowed,
            current_state=self._state,
            target_state=target_state,
            reason=reason,
        )

    def transition(
        self,
        target_state: ExecutionGovernanceState,
    ) -> ExecutionGovernanceDecision:
        """
        Validate and apply a lifecycle transition.
        """

        decision = self.evaluate(
            target_state
        )

        if decision.is_denied():
            return decision

        self._state = target_state

        return decision

    def transition_from_event(
        self,
        event_type: ExecutionEventType,
    ) -> ExecutionGovernanceDecision:
        """
        Apply a lifecycle transition represented
        by an execution event type.

        The authorization lifecycle state is represented
        separately because authorization itself is not
        an ExecutionEventType.
        """

        if not isinstance(
            event_type,
            ExecutionEventType,
        ):
            raise TypeError(
                "event_type must be an "
                "ExecutionEventType."
            )

        target_state = self._EVENT_TO_STATE[
            event_type
        ]

        return self.transition(
            target_state
        )

    def reset(self) -> None:
        """
        Reset lifecycle governance to CREATED.
        """

        self._state = (
            ExecutionGovernanceState.CREATED
        )
