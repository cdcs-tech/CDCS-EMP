"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.1

Execution lifecycle governance contract tests.
"""

import pytest

from app.core.execution import (
    ExecutionGovernanceContract,
    ExecutionGovernanceDecision,
    ExecutionGovernanceState,
)

from app.core.execution.events import (
    ExecutionEventType,
)


def test_governance_starts_in_created_state():
    """
    Execution lifecycle governance starts in CREATED.
    """

    governance = ExecutionGovernanceContract()

    assert (
        governance.state
        is ExecutionGovernanceState.CREATED
    )


def test_created_can_transition_to_authorized():
    """
    CREATED may transition to AUTHORIZED.
    """

    governance = ExecutionGovernanceContract()

    decision = governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    assert isinstance(
        decision,
        ExecutionGovernanceDecision,
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.AUTHORIZED
    )


def test_authorized_can_transition_to_started():
    """
    AUTHORIZED may transition to STARTED.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    decision = governance.transition(
        ExecutionGovernanceState.STARTED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.STARTED
    )


def test_started_can_complete():
    """
    STARTED may transition to COMPLETED.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    governance.transition(
        ExecutionGovernanceState.STARTED
    )

    decision = governance.transition(
        ExecutionGovernanceState.COMPLETED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.COMPLETED
    )


def test_started_can_fail():
    """
    STARTED may transition to FAILED.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    governance.transition(
        ExecutionGovernanceState.STARTED
    )

    decision = governance.transition(
        ExecutionGovernanceState.FAILED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.FAILED
    )


def test_authorized_can_be_denied():
    """
    AUTHORIZED may transition to DENIED.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    decision = governance.transition(
        ExecutionGovernanceState.DENIED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.DENIED
    )


def test_invalid_transition_is_rejected():
    """
    Invalid lifecycle transitions are rejected
    without changing state.
    """

    governance = ExecutionGovernanceContract()

    decision = governance.transition(
        ExecutionGovernanceState.COMPLETED
    )

    assert decision.is_denied()

    assert (
        decision.current_state
        is ExecutionGovernanceState.CREATED
    )

    assert (
        decision.target_state
        is ExecutionGovernanceState.COMPLETED
    )

    assert (
        "Invalid execution lifecycle transition"
        in decision.reason
    )

    assert (
        governance.state
        is ExecutionGovernanceState.CREATED
    )


def test_terminal_state_cannot_transition():
    """
    Terminal lifecycle states cannot transition
    to another execution state.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    governance.transition(
        ExecutionGovernanceState.STARTED
    )

    governance.transition(
        ExecutionGovernanceState.COMPLETED
    )

    decision = governance.transition(
        ExecutionGovernanceState.STARTED
    )

    assert decision.is_denied()

    assert (
        governance.state
        is ExecutionGovernanceState.COMPLETED
    )


def test_event_started_maps_to_started_state():
    """
    STARTED execution events map to STARTED
    governance state.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    decision = governance.transition_from_event(
        ExecutionEventType.STARTED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.STARTED
    )


def test_event_completed_maps_to_completed_state():
    """
    COMPLETED execution events map to COMPLETED
    governance state.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    governance.transition(
        ExecutionGovernanceState.STARTED
    )

    decision = governance.transition_from_event(
        ExecutionEventType.COMPLETED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.COMPLETED
    )


def test_event_failed_maps_to_failed_state():
    """
    FAILED execution events map to FAILED
    governance state.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    governance.transition(
        ExecutionGovernanceState.STARTED
    )

    decision = governance.transition_from_event(
        ExecutionEventType.FAILED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.FAILED
    )


def test_event_denied_maps_to_denied_state():
    """
    DENIED execution events map to DENIED
    governance state.
    """

    governance = ExecutionGovernanceContract()

    decision = governance.transition_from_event(
        ExecutionEventType.DENIED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.DENIED
    )


def test_can_transition_does_not_change_state():
    """
    can_transition() is a non-mutating evaluation.
    """

    governance = ExecutionGovernanceContract()

    assert governance.can_transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    assert (
        governance.state
        is ExecutionGovernanceState.CREATED
    )


def test_evaluate_does_not_change_state():
    """
    evaluate() is a non-mutating governance check.
    """

    governance = ExecutionGovernanceContract()

    decision = governance.evaluate(
        ExecutionGovernanceState.AUTHORIZED
    )

    assert decision.is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.CREATED
    )


def test_reset_returns_governance_to_created():
    """
    Governance can be reset to CREATED.
    """

    governance = ExecutionGovernanceContract()

    governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    )

    governance.transition(
        ExecutionGovernanceState.STARTED
    )

    governance.transition(
        ExecutionGovernanceState.COMPLETED
    )

    governance.reset()

    assert (
        governance.state
        is ExecutionGovernanceState.CREATED
    )


@pytest.mark.parametrize(
    "invalid_state",
    [
        object(),
        None,
        "started",
        123,
    ],
)
def test_invalid_initial_state_is_rejected(
    invalid_state,
):
    """
    Invalid initial governance states are rejected.
    """

    with pytest.raises(
        TypeError,
        match="initial_state",
    ):
        ExecutionGovernanceContract(
            initial_state=invalid_state
        )


@pytest.mark.parametrize(
    "invalid_state",
    [
        object(),
        None,
        "started",
        123,
    ],
)
def test_invalid_transition_state_is_rejected(
    invalid_state,
):
    """
    Invalid transition targets are rejected.
    """

    governance = ExecutionGovernanceContract()

    with pytest.raises(
        TypeError,
        match="target_state",
    ):
        governance.transition(
            invalid_state
        )


def test_invalid_event_type_is_rejected():
    """
    transition_from_event() requires an
    ExecutionEventType.
    """

    governance = ExecutionGovernanceContract()

    with pytest.raises(
        TypeError,
        match="event_type",
    ):
        governance.transition_from_event(
            "execution.started"
        )


def test_denied_transition_does_not_mutate_state():
    """
    A denied transition must never mutate
    lifecycle state.
    """

    governance = ExecutionGovernanceContract()

    decision = governance.transition(
        ExecutionGovernanceState.COMPLETED
    )

    assert decision.is_denied()

    assert (
        governance.state
        is ExecutionGovernanceState.CREATED
    )


def test_governance_decision_exposes_transition_details():
    """
    Governance decisions expose sufficient
    information for callers to understand
    the evaluated transition.
    """

    governance = ExecutionGovernanceContract()

    decision = governance.evaluate(
        ExecutionGovernanceState.AUTHORIZED
    )

    assert (
        decision.current_state
        is ExecutionGovernanceState.CREATED
    )

    assert (
        decision.target_state
        is ExecutionGovernanceState.AUTHORIZED
    )

    assert decision.allowed is True

    assert decision.reason


def test_full_success_lifecycle():
    """
    The complete successful execution lifecycle
    is accepted.
    """

    governance = ExecutionGovernanceContract()

    assert governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    ).is_allowed()

    assert governance.transition(
        ExecutionGovernanceState.STARTED
    ).is_allowed()

    assert governance.transition(
        ExecutionGovernanceState.COMPLETED
    ).is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.COMPLETED
    )


def test_full_failure_lifecycle():
    """
    The complete failed execution lifecycle
    is accepted.
    """

    governance = ExecutionGovernanceContract()

    assert governance.transition(
        ExecutionGovernanceState.AUTHORIZED
    ).is_allowed()

    assert governance.transition(
        ExecutionGovernanceState.STARTED
    ).is_allowed()

    assert governance.transition(
        ExecutionGovernanceState.FAILED
    ).is_allowed()

    assert (
        governance.state
        is ExecutionGovernanceState.FAILED
    )
