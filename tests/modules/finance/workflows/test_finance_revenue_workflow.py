"""
Tests for the Finance Revenue workflow.
"""

import pytest

from app.modules.finance.workflows.finance_revenue import (
    FinanceRevenueWorkflow,
)


def test_finance_revenue_workflow_defines_expected_states():
    """Finance Revenue exposes its approved lifecycle states."""
    workflow = FinanceRevenueWorkflow()

    assert {
        state.name
        for state in workflow.states()
    } == {
        workflow.PENDING,
        workflow.POSTED,
    }


def test_finance_revenue_workflow_defines_expected_transition():
    """Finance Revenue exposes the single posting transition."""
    workflow = FinanceRevenueWorkflow()

    transitions = workflow.transitions()

    assert len(transitions) == 1

    transition = transitions[0]

    assert transition.source == workflow.PENDING
    assert transition.target == workflow.POSTED
    assert transition.action == workflow.ACTION_POST
    assert transition.metadata == {
        "operation": "finance_revenue.post",
        "terminal": True,
    }


def test_finance_revenue_workflow_allows_pending_to_posted():
    """PENDING may transition to POSTED."""
    workflow = FinanceRevenueWorkflow()

    assert workflow.can_transition(
        workflow.PENDING,
        workflow.POSTED,
    )


def test_finance_revenue_workflow_transition_returns_posted_state():
    """A valid posting transition returns the target state."""
    workflow = FinanceRevenueWorkflow()

    state = workflow.transition(
        workflow.PENDING,
        workflow.POSTED,
    )

    assert state.name == workflow.POSTED


@pytest.mark.parametrize(
    "source,target",
    [
        ("UNKNOWN", FinanceRevenueWorkflow.POSTED),
        (FinanceRevenueWorkflow.PENDING, "UNKNOWN"),
        (FinanceRevenueWorkflow.POSTED, FinanceRevenueWorkflow.PENDING),
        (
            FinanceRevenueWorkflow.POSTED,
            FinanceRevenueWorkflow.POSTED,
        ),
        (
            FinanceRevenueWorkflow.PENDING,
            FinanceRevenueWorkflow.PENDING,
        ),
    ],
)
def test_finance_revenue_workflow_rejects_invalid_transitions(
    source,
    target,
):
    """Invalid and reopening transitions must be rejected."""
    workflow = FinanceRevenueWorkflow()

    with pytest.raises(ValueError):
        workflow.transition(source, target)


def test_finance_revenue_workflow_posted_is_terminal():
    """POSTED has no outgoing transition."""
    workflow = FinanceRevenueWorkflow()

    outgoing = [
        transition
        for transition in workflow.transitions()
        if transition.source == workflow.POSTED
    ]

    assert outgoing == []
