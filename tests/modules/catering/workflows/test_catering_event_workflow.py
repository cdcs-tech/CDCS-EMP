"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Event Workflow Tests
"""

from app.modules.catering.workflows.catering_event import (
    CateringEventWorkflow,
)


def test_catering_event_workflow_defines_expected_states():
    workflow = CateringEventWorkflow()

    assert [state.name for state in workflow.states()] == [
        "REQUESTED",
        "QUOTED",
        "PENDING_CONFIRMATION",
        "CONFIRMED",
        "PLANNING",
        "READY",
        "IN_PRODUCTION",
        "DELIVERED",
        "COMPLETED",
        "CANCELLED",
    ]


def test_catering_event_workflow_defines_forward_lifecycle():
    workflow = CateringEventWorkflow()

    expected_transitions = [
        ("REQUESTED", "QUOTED"),
        ("QUOTED", "PENDING_CONFIRMATION"),
        ("PENDING_CONFIRMATION", "CONFIRMED"),
        ("CONFIRMED", "PLANNING"),
        ("PLANNING", "READY"),
        ("READY", "IN_PRODUCTION"),
        ("IN_PRODUCTION", "DELIVERED"),
        ("DELIVERED", "COMPLETED"),
    ]

    for source, target in expected_transitions:
        assert workflow.can_transition(
            source,
            target,
        )


def test_catering_event_workflow_defines_approved_cancellation_paths():
    workflow = CateringEventWorkflow()

    expected_cancellations = [
        ("REQUESTED", "CANCELLED"),
        ("QUOTED", "CANCELLED"),
        ("PENDING_CONFIRMATION", "CANCELLED"),
    ]

    for source, target in expected_cancellations:
        assert workflow.can_transition(
            source,
            target,
        )


def test_catering_event_workflow_does_not_allow_cancellation_after_confirmation():
    workflow = CateringEventWorkflow()

    assert not workflow.can_transition(
        "CONFIRMED",
        "CANCELLED",
    )

    assert not workflow.can_transition(
        "PLANNING",
        "CANCELLED",
    )

    assert not workflow.can_transition(
        "READY",
        "CANCELLED",
    )

    assert not workflow.can_transition(
        "IN_PRODUCTION",
        "CANCELLED",
    )

    assert not workflow.can_transition(
        "DELIVERED",
        "CANCELLED",
    )

    assert not workflow.can_transition(
        "COMPLETED",
        "CANCELLED",
    )


def test_catering_event_workflow_does_not_allow_backward_transitions():
    workflow = CateringEventWorkflow()

    backward_transitions = [
        ("QUOTED", "REQUESTED"),
        ("PENDING_CONFIRMATION", "QUOTED"),
        ("CONFIRMED", "PENDING_CONFIRMATION"),
        ("PLANNING", "CONFIRMED"),
        ("READY", "PLANNING"),
        ("IN_PRODUCTION", "READY"),
        ("DELIVERED", "IN_PRODUCTION"),
        ("COMPLETED", "DELIVERED"),
    ]

    for source, target in backward_transitions:
        assert not workflow.can_transition(
            source,
            target,
        )


def test_catering_event_workflow_transition_returns_expected_state():
    workflow = CateringEventWorkflow()

    result = workflow.transition(
        "CONFIRMED",
        "PLANNING",
    )

    assert result.name == "PLANNING"


def test_catering_event_workflow_transition_returns_cancelled_state():
    workflow = CateringEventWorkflow()

    result = workflow.transition(
        "PENDING_CONFIRMATION",
        "CANCELLED",
    )

    assert result.name == "CANCELLED"


def test_catering_event_workflow_rejects_invalid_transition():
    workflow = CateringEventWorkflow()

    try:
        workflow.transition(
            "COMPLETED",
            "PLANNING",
        )
    except ValueError as exc:
        assert "Invalid workflow transition" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid workflow transition to raise ValueError."
        )
