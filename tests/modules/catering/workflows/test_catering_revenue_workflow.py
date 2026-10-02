
"""
Tests for the Catering Revenue workflow.
"""

import pytest

from app.modules.catering.workflows import CateringRevenueWorkflow


def test_revenue_workflow_initial_state_is_draft():
    workflow = CateringRevenueWorkflow()

    assert workflow.get_state(
        CateringRevenueWorkflow.DRAFT
    ).name == CateringRevenueWorkflow.DRAFT


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (
            CateringRevenueWorkflow.DRAFT,
            CateringRevenueWorkflow.ELIGIBLE,
        ),
        (
            CateringRevenueWorkflow.ELIGIBLE,
            CateringRevenueWorkflow.RECOGNIZED,
        ),
        (
            CateringRevenueWorkflow.DRAFT,
            CateringRevenueWorkflow.CANCELLED,
        ),
        (
            CateringRevenueWorkflow.ELIGIBLE,
            CateringRevenueWorkflow.CANCELLED,
        ),
    ],
)
def test_revenue_workflow_accepts_defined_transitions(
    source,
    target,
):
    workflow = CateringRevenueWorkflow()

    result = workflow.transition(source, target)

    assert result.name == target


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (
            CateringRevenueWorkflow.DRAFT,
            CateringRevenueWorkflow.RECOGNIZED,
        ),
        (
            CateringRevenueWorkflow.RECOGNIZED,
            CateringRevenueWorkflow.CANCELLED,
        ),
        (
            CateringRevenueWorkflow.CANCELLED,
            CateringRevenueWorkflow.DRAFT,
        ),
        (
            CateringRevenueWorkflow.RECOGNIZED,
            CateringRevenueWorkflow.ELIGIBLE,
        ),
    ],
)
def test_revenue_workflow_rejects_undefined_transitions(
    source,
    target,
):
    workflow = CateringRevenueWorkflow()

    with pytest.raises(ValueError, match="Invalid workflow transition"):
        workflow.transition(source, target)
