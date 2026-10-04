"""
Tests for the Catering Event profitability composition service.
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.catering.services.event_profitability import (
    EventProfitabilityResult,
    EventProfitabilityService,
)


def build_service(
    *,
    event_repository: Mock | None = None,
    revenue_repository: Mock | None = None,
    association_repository: Mock | None = None,
    expense_repository: Mock | None = None,
) -> tuple[
    EventProfitabilityService,
    Mock,
    Mock,
    Mock,
    Mock,
]:
    """Build the profitability service with isolated repository mocks."""

    event_repository = (
        event_repository
        if event_repository is not None
        else Mock()
    )
    revenue_repository = (
        revenue_repository
        if revenue_repository is not None
        else Mock()
    )
    association_repository = (
        association_repository
        if association_repository is not None
        else Mock()
    )
    expense_repository = (
        expense_repository
        if expense_repository is not None
        else Mock()
    )

    service = EventProfitabilityService(
        catering_event_repository=event_repository,
        catering_revenue_repository=revenue_repository,
        expense_cost_association_repository=association_repository,
        expense_repository=expense_repository,
    )

    return (
        service,
        event_repository,
        revenue_repository,
        association_repository,
        expense_repository,
    )


def test_calculate_for_event_composes_revenue_and_consumed_costs():
    """Verify profitability is revenue less consumed Catering costs."""

    event = SimpleNamespace(
        id=42,
    )

    revenue = SimpleNamespace(
        event_id=42,
        revenue_reference="CAT-REV-C6.7-001",
        amount=Decimal("1250.00"),
        currency="USD",
    )

    consumed_association_one = SimpleNamespace(
        id=101,
        contribution_id="COST-CONTRIBUTION-001",
        expense_id=501,
    )

    consumed_association_two = SimpleNamespace(
        id=102,
        contribution_id="COST-CONTRIBUTION-002",
        expense_id=502,
    )

    expense_one = SimpleNamespace(
        id=501,
        amount=Decimal("150.00"),
    )

    expense_two = SimpleNamespace(
        id=502,
        amount=Decimal("100.00"),
    )

    service, event_repository, revenue_repository, association_repository, expense_repository = (
        build_service()
    )

    event_repository.get_by_id.return_value = event
    revenue_repository.get_recognized_by_event_id.return_value = revenue
    association_repository.get_consumed_by_catering_context.return_value = [
        consumed_association_one,
        consumed_association_two,
    ]
    expense_repository.get_by_id.side_effect = [
        expense_one,
        expense_two,
    ]

    result = service.calculate_for_event(42)

    assert isinstance(result, EventProfitabilityResult)

    assert result.event_id == 42
    assert result.event_reference == "EVENT-42"
    assert result.revenue_reference == "CAT-REV-C6.7-001"
    assert result.revenue_amount == Decimal("1250.00")
    assert result.currency == "USD"

    assert result.total_cost == Decimal("250.00")
    assert result.profit == Decimal("1000.00")

    assert len(result.cost_contributions) == 2

    assert result.cost_contributions[0].association_id == 101
    assert (
        result.cost_contributions[0].contribution_id
        == "COST-CONTRIBUTION-001"
    )
    assert result.cost_contributions[0].expense_id == 501
    assert (
        result.cost_contributions[0].expense_amount
        == Decimal("150.00")
    )

    assert result.cost_contributions[1].association_id == 102
    assert (
        result.cost_contributions[1].contribution_id
        == "COST-CONTRIBUTION-002"
    )
    assert result.cost_contributions[1].expense_id == 502
    assert (
        result.cost_contributions[1].expense_amount
        == Decimal("100.00")
    )

    revenue_repository.get_recognized_by_event_id.assert_called_once_with(
        42
    )

    association_repository.get_consumed_by_catering_context.assert_called_once_with(
        "CATERING_EVENT",
        "EVENT-42",
    )

    assert expense_repository.get_by_id.call_count == 2


def test_calculate_for_event_uses_expense_amount_as_authoritative_cost():
    """Verify cost amounts come from Expense rather than the association."""

    event = SimpleNamespace(
        id=42,
    )

    revenue = SimpleNamespace(
        event_id=42,
        revenue_reference="CAT-REV-C6.7-002",
        amount=Decimal("500.00"),
        currency="USD",
    )

    association = SimpleNamespace(
        id=201,
        contribution_id="COST-CONTRIBUTION-003",
        expense_id=601,
        amount=Decimal("9999.00"),
    )

    expense = SimpleNamespace(
        id=601,
        amount=Decimal("125.00"),
    )

    service, event_repository, revenue_repository, association_repository, expense_repository = (
        build_service()
    )

    event_repository.get_by_id.return_value = event
    revenue_repository.get_recognized_by_event_id.return_value = revenue
    association_repository.get_consumed_by_catering_context.return_value = [
        association
    ]
    expense_repository.get_by_id.return_value = expense

    result = service.calculate_for_event(42)

    assert result.total_cost == Decimal("125.00")
    assert result.profit == Decimal("375.00")
    assert (
        result.cost_contributions[0].expense_amount
        == Decimal("125.00")
    )


def test_calculate_for_event_excludes_eligible_but_unconsumed_costs():
    """Verify only consumed associations returned by the repository are included."""

    event = SimpleNamespace(
        id=42,
    )

    revenue = SimpleNamespace(
        event_id=42,
        revenue_reference="CAT-REV-C6.7-003",
        amount=Decimal("800.00"),
        currency="USD",
    )

    consumed_association = SimpleNamespace(
        id=301,
        contribution_id="COST-CONTRIBUTION-CONSUMED",
        expense_id=701,
    )

    expense = SimpleNamespace(
        id=701,
        amount=Decimal("200.00"),
    )

    service, event_repository, revenue_repository, association_repository, expense_repository = (
        build_service()
    )

    event_repository.get_by_id.return_value = event
    revenue_repository.get_recognized_by_event_id.return_value = revenue

    # The repository contract intentionally returns only CONSUMED
    # associations. An eligible association therefore never enters
    # profitability composition.
    association_repository.get_consumed_by_catering_context.return_value = [
        consumed_association
    ]

    expense_repository.get_by_id.return_value = expense

    result = service.calculate_for_event(42)

    assert result.total_cost == Decimal("200.00")
    assert result.profit == Decimal("600.00")
    assert len(result.cost_contributions) == 1

    association_repository.get_consumed_by_catering_context.assert_called_once_with(
        "CATERING_EVENT",
        "EVENT-42",
    )


def test_calculate_for_event_requires_existing_event():
    """Verify an unknown Event cannot produce profitability."""

    service, event_repository, revenue_repository, association_repository, expense_repository = (
        build_service()
    )

    event_repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Catering Event not found: 42",
    ):
        service.calculate_for_event(42)

    revenue_repository.get_recognized_by_event_id.assert_not_called()
    association_repository.get_consumed_by_catering_context.assert_not_called()
    expense_repository.get_by_id.assert_not_called()


def test_calculate_for_event_requires_recognized_revenue():
    """Verify profitability requires an already-recognized Catering Revenue."""

    event = SimpleNamespace(
        id=42,
    )

    service, event_repository, revenue_repository, association_repository, expense_repository = (
        build_service()
    )

    event_repository.get_by_id.return_value = event
    revenue_repository.get_recognized_by_event_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Recognized Catering Revenue not found for event: 42",
    ):
        service.calculate_for_event(42)

    association_repository.get_consumed_by_catering_context.assert_not_called()
    expense_repository.get_by_id.assert_not_called()


def test_calculate_for_event_requires_existing_expense_for_consumed_association():
    """Verify a consumed association must resolve to an Expense record."""

    event = SimpleNamespace(
        id=42,
    )

    revenue = SimpleNamespace(
        event_id=42,
        revenue_reference="CAT-REV-C6.7-004",
        amount=Decimal("800.00"),
        currency="USD",
    )

    association = SimpleNamespace(
        id=401,
        contribution_id="COST-CONTRIBUTION-MISSING",
        expense_id=801,
    )

    service, event_repository, revenue_repository, association_repository, expense_repository = (
        build_service()
    )

    event_repository.get_by_id.return_value = event
    revenue_repository.get_recognized_by_event_id.return_value = revenue
    association_repository.get_consumed_by_catering_context.return_value = [
        association
    ]
    expense_repository.get_by_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Expense not found for Catering cost association: 401",
    ):
        service.calculate_for_event(42)


def test_event_profitability_result_is_immutable():
    """Verify the profitability result cannot be mutated after creation."""

    result = EventProfitabilityResult(
        event_id=42,
        event_reference="EVENT-42",
        revenue_reference="CAT-REV-C6.7-005",
        revenue_amount=Decimal("1000.00"),
        currency="USD",
        cost_contributions=(),
        total_cost=Decimal("0.00"),
        profit=Decimal("1000.00"),
    )

    with pytest.raises(
        AttributeError,
    ):
        result.profit = Decimal("500.00")
