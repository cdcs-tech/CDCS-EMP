"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Tests for the Finance Revenue application service.
"""

from datetime import date
from unittest.mock import Mock

import pytest

from app.core.crud.transaction import (
    SimpleTransactionManager,
)
from app.modules.finance.models import FinanceRevenue
from app.modules.finance.services import FinanceRevenueService
from app.modules.finance.workflows import FinanceRevenueWorkflow


def build_revenue(
    status: str = FinanceRevenueWorkflow.PENDING,
    contribution_reference: str = "CONTRIBUTION-TEST-001",
) -> FinanceRevenue:
    """
    Build an unsaved Finance Revenue entity for service tests.
    """

    return FinanceRevenue(
        revenue_reference="FIN-REV-TEST-001",
        contribution_reference=contribution_reference,
        source_type="CATERING_REVENUE",
        source_reference="CAT-REV-TEST-001",
        amount=100,
        currency="USD",
        revenue_date=date(2026, 9, 30),
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


def test_consume_contribution_persists_new_revenue_as_pending():
    """
    A new contribution is persisted as a PENDING Finance Revenue record.
    """

    revenue = build_revenue()
    repository = Mock()
    repository.get_by_contribution_reference.return_value = None
    repository.add.return_value = revenue

    transaction_manager = SimpleTransactionManager()

    service = FinanceRevenueService(
        repository=repository,
        transaction_manager=transaction_manager,
    )

    result = service.consume_contribution(revenue)

    assert result is revenue
    assert revenue.status == FinanceRevenueWorkflow.PENDING
    assert transaction_manager.committed is True
    assert transaction_manager.rolled_back is False

    repository.get_by_contribution_reference.assert_called_once_with(
        "CONTRIBUTION-TEST-001"
    )
    repository.add.assert_called_once_with(revenue)


def test_consume_contribution_returns_existing_revenue():
    """
    An already-consumed contribution returns the existing Finance record.
    """

    incoming = build_revenue()
    existing = build_revenue(
        contribution_reference="CONTRIBUTION-TEST-001",
    )

    repository = Mock()
    repository.get_by_contribution_reference.return_value = existing

    transaction_manager = SimpleTransactionManager()

    service = FinanceRevenueService(
        repository=repository,
        transaction_manager=transaction_manager,
    )

    result = service.consume_contribution(incoming)

    assert result is existing
    assert transaction_manager.committed is True
    repository.add.assert_not_called()


def test_consume_contribution_normalizes_contribution_reference():
    """
    Contribution identity is normalized before Finance lookup/persistence.
    """

    revenue = build_revenue(
        contribution_reference="  CONTRIBUTION-TEST-001  ",
    )

    repository = Mock()
    repository.get_by_contribution_reference.return_value = None
    repository.add.return_value = revenue

    transaction_manager = SimpleTransactionManager()

    service = FinanceRevenueService(
        repository=repository,
        transaction_manager=transaction_manager,
    )

    service.consume_contribution(revenue)

    assert revenue.contribution_reference == "CONTRIBUTION-TEST-001"
    repository.get_by_contribution_reference.assert_called_once_with(
        "CONTRIBUTION-TEST-001"
    )


def test_consume_contribution_rejects_missing_contribution_reference():
    """
    Finance consumption requires a stable contribution identity.
    """

    revenue = build_revenue(
        contribution_reference="   ",
    )

    repository = Mock()
    transaction_manager = SimpleTransactionManager()

    service = FinanceRevenueService(
        repository=repository,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(ValueError):
        service.consume_contribution(revenue)

    repository.get_by_contribution_reference.assert_not_called()
    repository.add.assert_not_called()
    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is False


def test_consume_contribution_rolls_back_when_persistence_fails():
    """
    A persistence failure rolls back the Finance consumption transaction.
    """

    revenue = build_revenue()

    repository = Mock()
    repository.get_by_contribution_reference.return_value = None
    repository.add.side_effect = RuntimeError(
        "Finance Revenue persistence failed."
    )

    transaction_manager = SimpleTransactionManager()

    service = FinanceRevenueService(
        repository=repository,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(RuntimeError, match="Finance Revenue persistence failed."):
        service.consume_contribution(revenue)

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True

    repository.get_by_contribution_reference.assert_called_once_with(
        "CONTRIBUTION-TEST-001"
    )
    repository.add.assert_called_once_with(revenue)
