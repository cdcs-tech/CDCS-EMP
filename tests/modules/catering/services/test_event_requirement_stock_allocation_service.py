"""Contract tests for Event Requirement stock allocation service."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.catering.services.event_requirement_stock_allocation import (
    EventRequirementStockAllocationService,
)


def _build_service():
    repository = Mock()
    balance_repository = Mock()
    requirement_repository = Mock()
    stock_item_repository = Mock()

    service = EventRequirementStockAllocationService(
        repository=repository,
        balance_repository=balance_repository,
        requirement_repository=requirement_repository,
        stock_item_repository=stock_item_repository,
    )

    return (
        service,
        repository,
        balance_repository,
        requirement_repository,
        stock_item_repository,
    )


def test_allocate_rejects_non_positive_quantity():
    service, _, _, _, _ = _build_service()

    with pytest.raises(ValueError, match="positive"):
        service.allocate(
            event_requirement_id=1,
            stock_item_id=2,
            location_id=3,
            quantity=Decimal("0"),
            unit="kg",
            idempotency_key="alloc-001",
        )


def test_allocate_requires_unit():
    service, _, _, _, _ = _build_service()

    with pytest.raises(ValueError, match="unit"):
        service.allocate(
            event_requirement_id=1,
            stock_item_id=2,
            location_id=3,
            quantity=Decimal("1"),
            unit=" ",
            idempotency_key="alloc-002",
        )


def test_allocate_requires_idempotency_key():
    service, _, _, _, _ = _build_service()

    with pytest.raises(ValueError, match="idempotency"):
        service.allocate(
            event_requirement_id=1,
            stock_item_id=2,
            location_id=3,
            quantity=Decimal("1"),
            unit="kg",
            idempotency_key=" ",
        )


def test_release_requires_existing_allocation():
    service, repository, _, _, _ = _build_service()
    repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match="allocation"):
        service.release(allocation_id=999)


def test_existing_identical_idempotency_request_returns_allocation():
    service, repository, _, _, _ = _build_service()
    allocation = SimpleNamespace(
        event_requirement_id=1,
        stock_item_id=2,
        location_id=3,
        quantity=Decimal("2.000"),
        unit="kg",
        idempotency_key="alloc-005",
        status="ACTIVE",
    )
    repository.get_by_idempotency_key.return_value = allocation

    result = service.allocate(
        event_requirement_id=1,
        stock_item_id=2,
        location_id=3,
        quantity=Decimal("2"),
        unit="kg",
        idempotency_key="alloc-005",
    )

    assert result is allocation
    repository.add.assert_not_called()


def test_reusing_idempotency_key_for_different_request_is_rejected():
    service, repository, _, _, _ = _build_service()
    repository.get_by_idempotency_key.return_value = SimpleNamespace(
        event_requirement_id=1,
        stock_item_id=2,
        location_id=3,
        quantity=Decimal("2"),
        unit="kg",
        idempotency_key="alloc-006",
        status="ACTIVE",
    )

    with pytest.raises(ValueError, match="different allocation"):
        service.allocate(
            event_requirement_id=1,
            stock_item_id=2,
            location_id=3,
            quantity=Decimal("3"),
            unit="kg",
            idempotency_key="alloc-006",
        )


def test_requirement_must_be_identified_before_allocation():
    service, _, _, requirement_repository, _ = _build_service()
    requirement_repository.get_by_id.return_value = SimpleNamespace(
        id=10,
        status="DRAFT",
        stock_item_id=2,
        unit="kg",
        quantity=Decimal("5"),
    )

    with pytest.raises(ValueError, match="IDENTIFIED"):
        service._validate_requirement(
            event_requirement_id=10,
            stock_item_id=2,
            unit="kg",
        )


def test_requirement_stock_item_mapping_must_match():
    service, _, _, requirement_repository, _ = _build_service()
    requirement_repository.get_by_id.return_value = SimpleNamespace(
        id=10,
        status="IDENTIFIED",
        stock_item_id=99,
        unit="kg",
        quantity=Decimal("5"),
    )

    with pytest.raises(ValueError, match="mapping"):
        service._validate_requirement(
            event_requirement_id=10,
            stock_item_id=2,
            unit="kg",
        )


def test_requirement_unit_must_match_allocation_unit():
    service, _, _, requirement_repository, _ = _build_service()
    requirement_repository.get_by_id.return_value = SimpleNamespace(
        id=10,
        status="IDENTIFIED",
        stock_item_id=2,
        unit="kg",
        quantity=Decimal("5"),
    )

    with pytest.raises(ValueError, match="unit"):
        service._validate_requirement(
            event_requirement_id=10,
            stock_item_id=2,
            unit="litre",
        )


def test_stock_item_product_unit_must_match_allocation_unit():
    service, _, _, _, stock_item_repository = _build_service()
    stock_item_repository.get_by_id.return_value = SimpleNamespace(
        id=2,
        product=SimpleNamespace(unit="litre"),
    )

    with pytest.raises(ValueError, match="Product unit"):
        service._validate_stock_item_unit(
            stock_item_id=2,
            unit="kg",
        )


def test_stock_item_product_unit_comparison_normalizes_case_and_spaces():
    service, _, _, _, stock_item_repository = _build_service()
    stock_item_repository.get_by_id.return_value = SimpleNamespace(
        id=2,
        product=SimpleNamespace(unit=" KG "),
    )

    service._validate_stock_item_unit(
        stock_item_id=2,
        unit="kg",
    )
