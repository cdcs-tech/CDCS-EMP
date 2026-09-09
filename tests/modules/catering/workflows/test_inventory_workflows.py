"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory Workflow Tests
"""

from app.modules.catering.workflows import (
    StockMovementWorkflow,
    StockTransferWorkflow,
)


def test_stock_movement_workflow_defines_expected_states():
    workflow = StockMovementWorkflow()

    assert [state.name for state in workflow.states()] == [
        "DRAFT",
        "POSTED",
    ]


def test_stock_movement_workflow_defines_post_transition():
    workflow = StockMovementWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "POSTED",
    )

    assert not workflow.can_transition(
        "POSTED",
        "DRAFT",
    )


def test_stock_movement_workflow_transition_returns_posted_state():
    workflow = StockMovementWorkflow()

    result = workflow.transition(
        "DRAFT",
        "POSTED",
    )

    assert result.name == "POSTED"


def test_stock_transfer_workflow_defines_expected_states():
    workflow = StockTransferWorkflow()

    assert [state.name for state in workflow.states()] == [
        "DRAFT",
        "POSTED",
    ]


def test_stock_transfer_workflow_defines_post_transition():
    workflow = StockTransferWorkflow()

    assert workflow.can_transition(
        "DRAFT",
        "POSTED",
    )

    assert not workflow.can_transition(
        "POSTED",
        "DRAFT",
    )


def test_stock_transfer_workflow_transition_returns_posted_state():
    workflow = StockTransferWorkflow()

    result = workflow.transition(
        "DRAFT",
        "POSTED",
    )

    assert result.name == "POSTED"
