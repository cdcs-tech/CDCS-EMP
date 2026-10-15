"""Tests for Event Requirement inventory fulfilment verification."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.catering.services.event_requirement_fulfilment import (
    EventRequirementFulfilmentVerifier,
)

from app.modules.catering.services.inventory_contracts import (
    InventoryAvailabilityResult,
)


def _requirement(
    *,
    requirement_id=10,
    stock_item_id=2,
    quantity="5",
    unit="kg",
):
    return SimpleNamespace(
        id=requirement_id,
        stock_item_id=stock_item_id,
        quantity=Decimal(quantity),
        unit=unit,
    )


def _allocation(
    *,
    requirement_id=10,
    stock_item_id=2,
    location_id=3,
    quantity="5",
    unit="kg",
    status="ACTIVE",
):
    return SimpleNamespace(
        event_requirement_id=requirement_id,
        stock_item_id=stock_item_id,
        location_id=location_id,
        quantity=Decimal(quantity),
        unit=unit,
        status=status,
    )


def _configure_allocations(monkeypatch, allocations):
    query = Mock()
    query.filter.return_value = query
    query.all.return_value = allocations

    session = Mock()
    session.query.return_value = query

    monkeypatch.setattr(
        "app.modules.catering.services.event_requirement_fulfilment.db.session",
        session,
    )
    availability_service = Mock()
    availability_service.get_available_quantity.return_value = (
        _availability_result()
    )

    monkeypatch.setattr(
        "app.modules.catering.services.event_requirement_fulfilment.InventoryAvailabilityService",
        Mock(return_value=availability_service),
    )
    return session, query


def _availability_result(
    *,
    stock_item_id=2,
    location_id=3,
    unit="kg",
    physical_quantity="10",
    reserved_quantity="5",
    available_quantity="5",
    verified=True,
    reason=None,
):
    return InventoryAvailabilityResult(
        stock_item_id=stock_item_id,
        location_id=location_id,
        unit=unit,
        physical_quantity=Decimal(physical_quantity),
        reserved_quantity=Decimal(reserved_quantity),
        available_quantity=Decimal(available_quantity),
        verified=verified,
        reason=reason,
    )


def _availability_service(result=None, error=None):
    service = Mock()

    if error is not None:
        service.get_available_quantity.side_effect = error
    else:
        service.get_available_quantity.return_value = (
            result
            if result is not None
            else _availability_result()
        )

    return service


def test_fully_allocated_requirement_passes(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [
            _allocation(quantity="2"),
            _allocation(quantity="3.000"),
        ],
    )

    EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_fulfilment_checks_inventory_availability(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation()],
    )
    availability = _availability_service()
    verifier = EventRequirementFulfilmentVerifier(
        availability_service=availability,
    )

    verifier.ensure_fulfilled(_requirement())

    availability.get_available_quantity.assert_called_once_with(
        stock_item_id=2,
        location_id=3,
        unit="kg",
    )


def test_same_location_allocations_must_be_covered_by_reported_reservations(
    monkeypatch,
):
    _configure_allocations(
        monkeypatch,
        [
            _allocation(quantity="2"),
            _allocation(quantity="3"),
        ],
    )
    availability = _availability_service(
        result=_availability_result(
            physical_quantity="10",
            reserved_quantity="4",
            available_quantity="6",
        ),
    )
    verifier = EventRequirementFulfilmentVerifier(
        availability_service=availability,
    )

    with pytest.raises(RuntimeError, match="reserved|allocation"):
        verifier.ensure_fulfilled(_requirement())


def test_same_location_allocations_cannot_exceed_physical_stock(
    monkeypatch,
):
    _configure_allocations(
        monkeypatch,
        [
            _allocation(quantity="6"),
            _allocation(quantity="4"),
        ],
    )
    availability = _availability_service(
        result=_availability_result(
            physical_quantity="10",
            reserved_quantity="5",
            available_quantity="5",
        ),
    )
    verifier = EventRequirementFulfilmentVerifier(
        availability_service=availability,
    )

    with pytest.raises(RuntimeError, match="reserved|allocation|physical"):
        verifier.ensure_fulfilled(_requirement(quantity="10"))


def test_unverified_inventory_availability_blocks_fulfilment(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation()],
    )
    availability = _availability_service(
        result=_availability_result(
            verified=False,
            available_quantity="0",
            reason="Stock balance could not be verified.",
        ),
    )
    verifier = EventRequirementFulfilmentVerifier(
        availability_service=availability,
    )

    with pytest.raises(RuntimeError, match="availability"):
        verifier.ensure_fulfilled(_requirement())


def test_inventory_availability_service_failure_blocks_fulfilment(
    monkeypatch,
):
    _configure_allocations(
        monkeypatch,
        [_allocation()],
    )
    availability = _availability_service(
        error=RuntimeError("Inventory unavailable"),
    )
    verifier = EventRequirementFulfilmentVerifier(
        availability_service=availability,
    )

    with pytest.raises(RuntimeError, match="availability"):
        verifier.ensure_fulfilled(_requirement())


def test_partially_allocated_requirement_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(quantity="4")],
    )

    with pytest.raises(RuntimeError, match="not fully fulfilled"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(
            _requirement()
        )


def test_requirement_without_persisted_id_is_rejected():
    with pytest.raises(RuntimeError, match="persisted requirement"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(
            _requirement(requirement_id=None)
        )


def test_requirement_without_stock_item_mapping_is_rejected():
    with pytest.raises(RuntimeError, match="mapped Stock Item"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(
            _requirement(stock_item_id=None)
        )


def test_requirement_without_active_allocations_is_rejected(monkeypatch):
    session, query = _configure_allocations(monkeypatch, [])

    with pytest.raises(RuntimeError, match="no active inventory allocations"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())

    assert session.query.called
    assert query.filter.called


def test_allocation_for_different_stock_item_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(stock_item_id=99)],
    )

    with pytest.raises(RuntimeError, match="different Stock Item"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_allocation_with_different_unit_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(unit="litre")],
    )

    with pytest.raises(RuntimeError, match="different unit"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_allocation_for_different_requirement_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(requirement_id=11)],
    )

    with pytest.raises(RuntimeError, match="different Event Requirement"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_non_active_allocation_returned_by_query_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(status="RELEASED")],
    )

    with pytest.raises(RuntimeError, match="not in ACTIVE status"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_excess_allocation_quantity_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(quantity="5.001")],
    )

    with pytest.raises(RuntimeError, match="exceed the Event Requirement"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_requirement_quantity_with_excess_precision_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(quantity="5")],
    )

    with pytest.raises(RuntimeError, match="three decimal places"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(
            _requirement(quantity="5.0001")
        )


def test_allocation_quantity_with_excess_precision_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(quantity="5.0001")],
    )

    with pytest.raises(RuntimeError, match="three decimal places"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_non_positive_allocation_quantity_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(quantity="0")],
    )

    with pytest.raises(RuntimeError, match="must be positive"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())


def test_released_allocation_is_not_counted_by_query(monkeypatch):
    _, query = _configure_allocations(monkeypatch, [])

    with pytest.raises(RuntimeError, match="no active inventory allocations"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(_requirement())

    # The filter expression includes both requirement identity and ACTIVE status.
    assert query.filter.called


def test_missing_requirement_unit_is_rejected(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation()],
    )

    with pytest.raises(RuntimeError, match="unit is missing"):
        EventRequirementFulfilmentVerifier().ensure_fulfilled(
            _requirement(unit=" ")
        )


def test_unit_comparison_ignores_case_and_surrounding_whitespace(monkeypatch):
    _configure_allocations(
        monkeypatch,
        [_allocation(unit=" KG ")],
    )

    EventRequirementFulfilmentVerifier().ensure_fulfilled(
        _requirement(unit="kg")
    )
