"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.2

Execution lifecycle governance and safeguard tests.
"""

import pytest

from app.core.execution import (
    ExecutionContractException,
    ExecutionLifecycle,
    ExecutionLifecycleState,
)


def test_lifecycle_starts_in_pending_state():
    """
    A new execution lifecycle starts in PENDING.
    """

    lifecycle = ExecutionLifecycle()

    assert (
        lifecycle.state
        is ExecutionLifecycleState.PENDING
    )

    assert lifecycle.is_terminal() is False


def test_pending_can_transition_to_running():
    """
    PENDING may transition to RUNNING.
    """

    lifecycle = ExecutionLifecycle()

    assert lifecycle.can_transition(
        ExecutionLifecycleState.RUNNING
    )

    lifecycle.transition(
        ExecutionLifecycleState.RUNNING
    )

    assert (
        lifecycle.state
        is ExecutionLifecycleState.RUNNING
    )


@pytest.mark.parametrize(
    "target",
    [
        ExecutionLifecycleState.COMPLETED,
        ExecutionLifecycleState.FAILED,
        ExecutionLifecycleState.DENIED,
    ],
)
def test_running_can_transition_to_terminal_states(target):
    """
    RUNNING may transition to each valid terminal state.
    """

    lifecycle = ExecutionLifecycle(
        ExecutionLifecycleState.RUNNING
    )

    assert lifecycle.can_transition(target)

    lifecycle.transition(target)

    assert lifecycle.state is target
    assert lifecycle.is_terminal() is True


def test_pending_cannot_skip_running():
    """
    PENDING cannot transition directly to a terminal state.
    """

    lifecycle = ExecutionLifecycle()

    with pytest.raises(
        ExecutionContractException,
        match="Invalid execution lifecycle transition",
    ):
        lifecycle.transition(
            ExecutionLifecycleState.COMPLETED
        )


@pytest.mark.parametrize(
    "target",
    [
        ExecutionLifecycleState.PENDING,
        ExecutionLifecycleState.RUNNING,
    ],
)
def test_terminal_state_cannot_transition(target):
    """
    Terminal states cannot transition further.
    """

    for terminal_state in (
        ExecutionLifecycleState.COMPLETED,
        ExecutionLifecycleState.FAILED,
        ExecutionLifecycleState.DENIED,
    ):
        lifecycle = ExecutionLifecycle(
            terminal_state
        )

        assert lifecycle.is_terminal() is True
        assert lifecycle.can_transition(target) is False

        with pytest.raises(
            ExecutionContractException,
            match="Invalid execution lifecycle transition",
        ):
            lifecycle.transition(target)


def test_invalid_initial_state_is_rejected():
    """
    Invalid initial lifecycle states are rejected.
    """

    with pytest.raises(
        ExecutionContractException,
        match="Execution lifecycle state",
    ):
        ExecutionLifecycle("pending")


def test_invalid_transition_state_is_rejected():
    """
    Invalid transition targets are rejected.
    """

    lifecycle = ExecutionLifecycle()

    with pytest.raises(
        ExecutionContractException,
        match="Execution lifecycle state",
    ):
        lifecycle.can_transition("running")


def test_invalid_transition_cannot_change_state():
    """
    A rejected transition leaves the current state unchanged.
    """

    lifecycle = ExecutionLifecycle(
        ExecutionLifecycleState.RUNNING
    )

    with pytest.raises(
        ExecutionContractException
    ):
        lifecycle.transition(
            ExecutionLifecycleState.PENDING
        )

    assert (
        lifecycle.state
        is ExecutionLifecycleState.RUNNING
    )


def test_terminal_state_cannot_be_reentered():
    """
    A terminal state cannot transition to itself.
    """

    lifecycle = ExecutionLifecycle(
        ExecutionLifecycleState.COMPLETED
    )

    with pytest.raises(
        ExecutionContractException,
        match="Invalid execution lifecycle transition",
    ):
        lifecycle.transition(
            ExecutionLifecycleState.COMPLETED
        )
