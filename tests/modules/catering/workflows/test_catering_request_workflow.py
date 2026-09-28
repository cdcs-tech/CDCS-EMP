"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Request Workflow Tests
"""

from app.modules.catering.workflows.catering_request import (
    CateringRequestWorkflow,
)


def test_catering_request_workflow_defines_expected_states():
    workflow = CateringRequestWorkflow()

    assert [state.name for state in workflow.states()] == [
        "DRAFT",
        "SUBMITTED",
        "CANCELLED",
    ]


def test_catering_request_workflow_defines_submit_transition():
    workflow = CateringRequestWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "SUBMITTED",
    )

    assert not workflow.can_transition(
        "SUBMITTED",
        "DRAFT",
    )


def test_catering_request_workflow_defines_draft_cancellation():
    workflow = CateringRequestWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "CANCELLED",
    )


def test_catering_request_workflow_defines_submitted_cancellation():
    workflow = CateringRequestWorkflow()

    assert workflow.can_transition(
        "SUBMITTED",
        "CANCELLED",
    )


def test_catering_request_workflow_does_not_allow_cancellation_to_active_state():
    workflow = CateringRequestWorkflow()

    assert not workflow.can_transition(
        "CANCELLED",
        "DRAFT",
    )

    assert not workflow.can_transition(
        "CANCELLED",
        "SUBMITTED",
    )


def test_catering_request_workflow_transition_returns_submitted_state():
    workflow = CateringRequestWorkflow()

    result = workflow.transition(
        "DRAFT",
        "SUBMITTED",
    )

    assert result.name == "SUBMITTED"


def test_catering_request_workflow_transition_returns_cancelled_state():
    workflow = CateringRequestWorkflow()

    result = workflow.transition(
        "SUBMITTED",
        "CANCELLED",
    )

    assert result.name == "CANCELLED"
