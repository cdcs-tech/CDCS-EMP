
"""Tests for Inventory-owned availability using injected test doubles."""

from dataclasses import dataclass, field
from decimal import Decimal

import pytest

from app.modules.catering.services.inventory_availability import (
    InventoryAvailabilityService,
)


@dataclass
class FakeProduct:
    unit: str = "kg"


@dataclass
class FakeStockItem:
    product: FakeProduct | None = field(default_factory=FakeProduct)
    is_active: bool = True


@dataclass
class FakeBalance:
    quantity: Decimal = Decimal("10.000")


class FakeStockItemRepository:
    def __init__(self, stock_item=FakeStockItem()):
        self.stock_item = stock_item

    def get_by_id(self, stock_item_id):
        return self.stock_item


class FakeBalanceRepository:
    def __init__(self, balance=FakeBalance()):
        self.balance = balance

    def get_by_stock_item_and_location(self, stock_item_id, location_id):
        return self.balance


class FakeAllocationQuery:
    def __init__(self, quantity=Decimal("2.000"), error=None):
        self.quantity = quantity
        self.error = error
        self.calls = []

    def __call__(self, *, stock_item_id, location_id, status):
        self.calls.append((stock_item_id, location_id, status))
        if self.error is not None:
            raise self.error
        return self.quantity


_DEFAULT_FIXTURE = object()

def make_service(
    *,
    stock_item=_DEFAULT_FIXTURE,
    balance=_DEFAULT_FIXTURE,
    allocated=Decimal("2.000"),
    allocation_error=None,
):
    if stock_item is _DEFAULT_FIXTURE:
        stock_item = FakeStockItem()
    if balance is _DEFAULT_FIXTURE:
        balance = FakeBalance()

    allocation_query = FakeAllocationQuery(
        quantity=allocated,
        error=allocation_error,
    )
    service = InventoryAvailabilityService(
        stock_item_repository=FakeStockItemRepository(stock_item),
        balance_repository=FakeBalanceRepository(balance),
        allocation_query=allocation_query,
    )
    return service, allocation_query


def test_returns_physical_stock_less_active_allocations():
    service, query = make_service()

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="KG",
    )

    assert result.verified is True
    assert result.physical_quantity == Decimal("10.000")
    assert result.reserved_quantity == Decimal("2.000")
    assert result.available_quantity == Decimal("8.000")
    assert result.unit == "kg"
    assert query.calls == [(1, 2, "ACTIVE")]


def test_zero_available_quantity_is_verified_when_fully_allocated():
    service, _ = make_service(allocated=Decimal("10.000"))

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is True
    assert result.available_quantity == Decimal("0.000")


def test_missing_stock_item_fails_closed():
    service, _ = make_service(stock_item=None)

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "does not exist" in result.reason


def test_inactive_stock_item_fails_closed():
    service, _ = make_service(stock_item=FakeStockItem(is_active=False))

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "inactive" in result.reason


def test_missing_product_fails_closed():
    service, _ = make_service(stock_item=FakeStockItem(product=None))

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "associated Product" in result.reason


def test_unit_mismatch_fails_closed():
    service, query = make_service()

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="litre",
    )

    assert result.verified is False
    assert "does not match" in result.reason
    assert query.calls == []


def test_missing_balance_fails_closed():
    service, _ = make_service(balance=None)

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "No stock balance" in result.reason


@pytest.mark.parametrize(
    "quantity",
    [
        Decimal("-1.000"),
        Decimal("NaN"),
        Decimal("1.0001"),
        "invalid",
    ],
)
def test_invalid_physical_balance_fails_closed(quantity):
    service, _ = make_service(balance=FakeBalance(quantity=quantity))

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "could not be verified" in result.reason


def test_invalid_allocation_total_fails_closed():
    service, _ = make_service(allocated=Decimal("-1.000"))

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False


def test_allocation_query_failure_fails_closed():
    service, _ = make_service(
        allocation_error=RuntimeError("allocation store unavailable"),
    )

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "could not be verified" in result.reason


def test_allocations_exceeding_physical_stock_fail_closed():
    service, _ = make_service(allocated=Decimal("11.000"))

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert result.verified is False
    assert "exceed" in result.reason
    assert result.available_quantity == Decimal("0.000")


@pytest.mark.parametrize(
    "stock_item_id, location_id, unit",
    [
        (0, 2, "kg"),
        (1, 0, "kg"),
        (True, 2, "kg"),
        (1, 2, " "),
    ],
)
def test_invalid_arguments_are_rejected(stock_item_id, location_id, unit):
    service, _ = make_service()

    with pytest.raises(ValueError):
        service.get_available_quantity(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=unit,
        )


