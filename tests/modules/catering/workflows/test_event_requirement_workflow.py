"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Event Requirement Workflow Tests
"""

from app.modules.catering.workflows import (
    EventRequirementWorkflow,
)


def test_event_requirement_workflow_defines_expected_states():
    workflow = EventRequirementWorkflow()

    assert [state.name for state in workflow.states()] == [
        "DRAFT",
        "IDENTIFIED",
        "READY",
        "CANCELLED",
    ]


def test_event_requirement_workflow_defines_identify_transition():
    workflow = EventRequirementWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "IDENTIFIED",
    )

    assert not workflow.can_transition(
        "IDENTIFIED",
        "DRAFT",
    )


def test_event_requirement_workflow_defines_ready_transition():
    workflow = EventRequirementWorkflow()

    assert workflow.can_transition(
        "IDENTIFIED",
        "READY",
    )

    assert not workflow.can_transition(
        "READY",
        "IDENTIFIED",
    )


def test_event_requirement_workflow_defines_draft_cancellation():
    workflow = EventRequirementWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "CANCELLED",
    )


def test_event_requirement_workflow_defines_identified_cancellation():
    workflow = EventRequirementWorkflow()

    assert workflow.can_transition(
        "IDENTIFIED",
        "CANCELLED",
    )


def test_event_requirement_workflow_does_not_allow_cancellation_from_ready():
    workflow = EventRequirementWorkflow()

    assert not workflow.can_transition(
        "READY",
        "CANCELLED",
    )


def test_event_requirement_workflow_does_not_allow_cancellation_from_cancelled():
    workflow = EventRequirementWorkflow()

    assert not workflow.can_transition(
        "CANCELLED",
        "DRAFT",
    )

    assert not workflow.can_transition(
        "CANCELLED",
        "IDENTIFIED",
    )

    assert not workflow.can_transition(
        "CANCELLED",
        "READY",
    )


def test_event_requirement_workflow_does_not_allow_backward_transitions():
    workflow = EventRequirementWorkflow()

    backward_transitions = [
        ("IDENTIFIED", "DRAFT"),
        ("READY", "IDENTIFIED"),
        ("READY", "DRAFT"),
    ]

    for source, target in backward_transitions:
        assert not workflow.can_transition(
            source,
            target,
        )


def test_event_requirement_workflow_transition_returns_identified_state():
    workflow = EventRequirementWorkflow()

    result = workflow.transition(
        "DRAFT",
        "IDENTIFIED",
    )

    assert result.name == "IDENTIFIED"


def test_event_requirement_workflow_transition_returns_ready_state():
    workflow = EventRequirementWorkflow()

    result = workflow.transition(
        "IDENTIFIED",
        "READY",
    )

    assert result.name == "READY"


def test_event_requirement_workflow_transition_returns_cancelled_state():
    workflow = EventRequirementWorkflow()

    result = workflow.transition(
        "IDENTIFIED",
        "CANCELLED",
    )

    assert result.name == "CANCELLED"


def test_event_requirement_workflow_rejects_invalid_transition():
    workflow = EventRequirementWorkflow()

    try:
        workflow.transition(
            "READY",
            "DRAFT",
        )
    except ValueError as exc:
        assert "Invalid workflow transition" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid workflow transition to raise ValueError."
        )
