"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Quotation Workflow Tests
"""

from app.modules.catering.workflows.catering_quotation import (
    CateringQuotationWorkflow,
)


def test_catering_quotation_workflow_defines_expected_states():
    workflow = CateringQuotationWorkflow()

    assert [state.name for state in workflow.states()] == [
        "DRAFT",
        "ISSUED",
        "ACCEPTED",
        "DECLINED",
        "EXPIRED",
    ]


def test_catering_quotation_workflow_defines_approved_transitions():
    workflow = CateringQuotationWorkflow()

    expected_transitions = [
        ("DRAFT", "ISSUED"),
        ("ISSUED", "ACCEPTED"),
        ("ISSUED", "DECLINED"),
        ("ISSUED", "EXPIRED"),
    ]

    for source, target in expected_transitions:
        assert workflow.can_transition(
            source,
            target,
        )


def test_catering_quotation_workflow_does_not_allow_direct_draft_terminal_transitions():
    workflow = CateringQuotationWorkflow()

    assert not workflow.can_transition(
        "DRAFT",
        "ACCEPTED",
    )

    assert not workflow.can_transition(
        "DRAFT",
        "DECLINED",
    )

    assert not workflow.can_transition(
        "DRAFT",
        "EXPIRED",
    )


def test_catering_quotation_workflow_does_not_allow_backward_transitions():
    workflow = CateringQuotationWorkflow()

    backward_transitions = [
        ("ISSUED", "DRAFT"),
        ("ACCEPTED", "ISSUED"),
        ("DECLINED", "ISSUED"),
        ("EXPIRED", "ISSUED"),
    ]

    for source, target in backward_transitions:
        assert not workflow.can_transition(
            source,
            target,
        )


def test_catering_quotation_workflow_does_not_allow_transitions_from_terminal_states():
    workflow = CateringQuotationWorkflow()

    terminal_states = [
        "ACCEPTED",
        "DECLINED",
        "EXPIRED",
    ]

    active_states = [
        "DRAFT",
        "ISSUED",
    ]

    for terminal_state in terminal_states:
        for target_state in active_states:
            assert not workflow.can_transition(
                terminal_state,
                target_state,
            )


def test_catering_quotation_workflow_transition_returns_issued_state():
    workflow = CateringQuotationWorkflow()

    result = workflow.transition(
        "DRAFT",
        "ISSUED",
    )

    assert result.name == "ISSUED"


def test_catering_quotation_workflow_transition_returns_accepted_state():
    workflow = CateringQuotationWorkflow()

    result = workflow.transition(
        "ISSUED",
        "ACCEPTED",
    )

    assert result.name == "ACCEPTED"


def test_catering_quotation_workflow_transition_returns_declined_state():
    workflow = CateringQuotationWorkflow()

    result = workflow.transition(
        "ISSUED",
        "DECLINED",
    )

    assert result.name == "DECLINED"


def test_catering_quotation_workflow_transition_returns_expired_state():
    workflow = CateringQuotationWorkflow()

    result = workflow.transition(
        "ISSUED",
        "EXPIRED",
    )

    assert result.name == "EXPIRED"


def test_catering_quotation_workflow_rejects_invalid_transition():
    workflow = CateringQuotationWorkflow()

    try:
        workflow.transition(
            "DRAFT",
            "ACCEPTED",
        )
    except ValueError as exc:
        assert "Invalid workflow transition" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid workflow transition to raise ValueError."
        )
