"""
Tests for Expense Management workflow definition.
"""

import pytest

from app.modules.expense.workflows import (
    ACTION_APPROVE,
    ACTION_CLOSE,
    ACTION_REJECT,
    ACTION_RESUBMIT,
    ACTION_RETURN,
    ACTION_SUBMIT,
    APPROVED,
    CLOSED,
    DRAFT,
    REJECTED,
    RETURNED,
    SUBMITTED,
    ExpenseWorkflow,
)


def test_expense_workflow_defines_expected_states():
    """
    ExpenseWorkflow defines exactly the six approved lifecycle states.
    """

    workflow = ExpenseWorkflow()

    assert [state.name for state in workflow.states()] == [
        DRAFT,
        SUBMITTED,
        RETURNED,
        APPROVED,
        REJECTED,
        CLOSED,
    ]


def test_expense_workflow_defines_expected_transitions():
    """
    ExpenseWorkflow defines exactly the six approved transitions.
    """

    workflow = ExpenseWorkflow()

    assert [
        (
            transition.source,
            transition.target,
            transition.action,
        )
        for transition in workflow.transitions()
    ] == [
        (DRAFT, SUBMITTED, ACTION_SUBMIT),
        (SUBMITTED, APPROVED, ACTION_APPROVE),
        (SUBMITTED, REJECTED, ACTION_REJECT),
        (SUBMITTED, RETURNED, ACTION_RETURN),
        (RETURNED, SUBMITTED, ACTION_RESUBMIT),
        (APPROVED, CLOSED, ACTION_CLOSE),
    ]


def test_expense_workflow_defines_expected_operation_metadata():
    """
    ExpenseWorkflow exposes the approved operation identities.
    """

    workflow = ExpenseWorkflow()

    assert [
        transition.metadata["operation"]
        for transition in workflow.transitions()
    ] == [
        "expense.submit",
        "expense.approve",
        "expense.reject",
        "expense.return",
        "expense.resubmit",
        "expense.close",
    ]


def test_expense_workflow_defines_expected_terminal_metadata():
    """
    Only REJECTED and CLOSED transitions are terminal.
    """

    workflow = ExpenseWorkflow()

    assert [
        transition.metadata["terminal"]
        for transition in workflow.transitions()
    ] == [
        False,
        False,
        True,
        False,
        False,
        True,
    ]


@pytest.mark.parametrize(
    "source,target",
    [
        (DRAFT, SUBMITTED),
        (SUBMITTED, APPROVED),
        (SUBMITTED, REJECTED),
        (SUBMITTED, RETURNED),
        (RETURNED, SUBMITTED),
        (APPROVED, CLOSED),
    ],
)
def test_expense_workflow_accepts_approved_transitions(
    source,
    target,
):
    """
    ExpenseWorkflow accepts every approved transition.
    """

    workflow = ExpenseWorkflow()

    assert workflow.can_transition(
        source,
        target,
    )


@pytest.mark.parametrize(
    "source,target",
    [
        (DRAFT, APPROVED),
        (DRAFT, REJECTED),
        (SUBMITTED, CLOSED),
        (RETURNED, APPROVED),
        (APPROVED, REJECTED),
        (REJECTED, DRAFT),
        (CLOSED, DRAFT),
    ],
)
def test_expense_workflow_rejects_unapproved_transitions(
    source,
    target,
):
    """
    ExpenseWorkflow rejects transitions outside the approved lifecycle.
    """

    workflow = ExpenseWorkflow()

    assert not workflow.can_transition(
        source,
        target,
    )


def test_expense_workflow_transition_returns_target_state():
    """
    A valid transition returns the registered target WorkflowState.
    """

    workflow = ExpenseWorkflow()

    state = workflow.transition(
        DRAFT,
        SUBMITTED,
    )

    assert state.name == SUBMITTED


def test_expense_workflow_transition_rejects_invalid_transition():
    """
    Invalid Expense workflow transitions raise ValueError.
    """

    workflow = ExpenseWorkflow()

    with pytest.raises(ValueError):
        workflow.transition(
            DRAFT,
            APPROVED,
        )


def test_expense_workflow_has_no_reopening_transition():
    """
    Terminal Expense states cannot transition to another state.
    """

    workflow = ExpenseWorkflow()

    assert not any(
        transition.source in {
            REJECTED,
            CLOSED,
        }
        for transition in workflow.transitions()
    )
