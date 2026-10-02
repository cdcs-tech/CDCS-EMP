"""
Tests for the Finance Revenue application service.
"""

from unittest.mock import Mock

import pytest

from app.modules.finance.models import FinanceRevenue
from app.modules.finance.services import FinanceRevenueService
from app.modules.finance.workflows import FinanceRevenueWorkflow


def build_revenue(
    status: str = FinanceRevenueWorkflow.PENDING,
) -> FinanceRevenue:
    """
    Build an unsaved Finance Revenue entity for service tests.
    """
    return FinanceRevenue(
        revenue_reference="FIN-REV-TEST-001",
        contribution_reference="CONTRIBUTION-TEST-001",
        source_type="CATERING_REVENUE",
        source_reference="CAT-REV-TEST-001",
        amount=100,
        currency="USD",
        revenue_date=__import__("datetime").date(2026, 9, 30),
        revenue_classification="CATERING",
        status=status,
    )


def test_finance_revenue_service_injects_repository_and_workflow():
    """The service accepts explicit repository and workflow dependencies."""
    repository = Mock()
    workflow = FinanceRevenueWorkflow()

    service = FinanceRevenueService(
        repository=repository,
        workflow=workflow,
    )

    assert service.repository is repository
    assert service.workflow is workflow


def test_post_transitions_pending_revenue_to_posted():
    """Posting applies the workflow's PENDING -> POSTED transition."""
    revenue = build_revenue()

    repository = Mock()
    repository.update.return_value = revenue

    service = FinanceRevenueService(
        repository=repository,
    )

    result = service.post(revenue)

    assert revenue.status == FinanceRevenueWorkflow.POSTED
    assert result is revenue
    repository.update.assert_called_once_with(revenue)


def test_post_rejects_invalid_revenue_status():
    """Posting a non-pending revenue record is rejected by the workflow."""
    revenue = build_revenue(
        status=FinanceRevenueWorkflow.POSTED,
    )

    repository = Mock()

    service = FinanceRevenueService(
        repository=repository,
    )

    with pytest.raises(ValueError):
        service.post(revenue)

    repository.update.assert_not_called()


def test_post_does_not_maintain_a_second_transition_matrix():
    """Service transition validity remains delegated to the workflow."""
    workflow = Mock(spec=FinanceRevenueWorkflow)
    repository = Mock()

    revenue = build_revenue()

    workflow.transition.return_value = Mock(
        name=FinanceRevenueWorkflow.POSTED,
    )

    service = FinanceRevenueService(
        repository=repository,
        workflow=workflow,
    )

    service.post(revenue)

    workflow.transition.assert_called_once_with(
        FinanceRevenueWorkflow.PENDING,
        FinanceRevenueWorkflow.POSTED,
    )
