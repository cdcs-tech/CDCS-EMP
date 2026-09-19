"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow tests.
"""

import pytest

from app.modules.procurement.workflows import (
    PurchaseOrderWorkflow,
)


def test_purchase_order_workflow_defines_approved_states():
    workflow = PurchaseOrderWorkflow()

    assert workflow.get_state(
        PurchaseOrderWorkflow.DRAFT
    ) is not None
    assert workflow.get_state(
        PurchaseOrderWorkflow.SUBMITTED
    ) is not None
    assert workflow.get_state(
        PurchaseOrderWorkflow.APPROVED
    ) is not None
    assert workflow.get_state(
        PurchaseOrderWorkflow.REJECTED
    ) is not None
    assert workflow.get_state(
        PurchaseOrderWorkflow.CANCELLED
    ) is not None


def test_purchase_order_workflow_defines_approved_transitions():
    workflow = PurchaseOrderWorkflow()

    transitions = {
        (
            transition.source,
            transition.target,
        ): transition
        for transition in workflow.transitions()
    }

    expected = {
        (
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.SUBMITTED,
        ): (
            PurchaseOrderWorkflow.ACTION_SUBMIT,
            "purchase_order.submit",
            False,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.APPROVED,
        ): (
            PurchaseOrderWorkflow.ACTION_APPROVE,
            "purchase_order.approve",
            False,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.REJECTED,
        ): (
            PurchaseOrderWorkflow.ACTION_REJECT,
            "purchase_order.reject",
            True,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.DRAFT,
        ): (
            PurchaseOrderWorkflow.ACTION_RETURN,
            "purchase_order.return",
            False,
        ),
        (
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.CANCELLED,
        ): (
            PurchaseOrderWorkflow.ACTION_CANCEL,
            "purchase_order.cancel",
            True,
        ),
    }

    assert len(transitions) == len(expected)

    for key, (
        action,
        operation,
        terminal,
    ) in expected.items():
        transition = transitions[key]

        assert transition.action == action
        assert (
            transition.metadata["operation"]
            == operation
        )
        assert (
            transition.metadata["terminal"]
            is terminal
        )


@pytest.mark.parametrize(
    (
        "source",
        "target",
        "expected_target",
    ),
    [
        (
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.SUBMITTED,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.APPROVED,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.REJECTED,
            PurchaseOrderWorkflow.REJECTED,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.DRAFT,
        ),
        (
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.CANCELLED,
            PurchaseOrderWorkflow.CANCELLED,
        ),
    ],
)
def test_purchase_order_workflow_executes_approved_transition(
    source,
    target,
    expected_target,
):
    workflow = PurchaseOrderWorkflow()

    state = workflow.transition(
        source,
        target,
    )

    assert state.name == expected_target


@pytest.mark.parametrize(
    (
        "source",
        "target",
    ),
    [
        (
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.APPROVED,
        ),
        (
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.REJECTED,
        ),
        (
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.CANCELLED,
        ),
        (
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.CANCELLED,
        ),
        (
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.SUBMITTED,
        ),
        (
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.DRAFT,
        ),
        (
            PurchaseOrderWorkflow.REJECTED,
            PurchaseOrderWorkflow.DRAFT,
        ),
        (
            PurchaseOrderWorkflow.CANCELLED,
            PurchaseOrderWorkflow.DRAFT,
        ),
    ],
)
def test_purchase_order_workflow_rejects_unapproved_transition(
    source,
    target,
):
    workflow = PurchaseOrderWorkflow()

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        workflow.transition(
            source,
            target,
        )
