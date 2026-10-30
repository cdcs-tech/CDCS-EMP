from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityValidationException


def _build_service(
    requirement,
    evidence_records=None,
    procurement_evidence=None,
):
    event = SimpleNamespace(id=6)

    requirement_repository = Mock()
    requirement_repository.get_by_event_id.return_value = [requirement]

    consumption_evidence_repository = Mock()
    consumption_evidence_repository.get_by_requirement_id.return_value = (
        evidence_records or []
    )

    procurement_evidence_resolver = Mock()
    procurement_evidence_resolver.get_receipt_status.return_value = (
        procurement_evidence
        if procurement_evidence is not None
        else SimpleNamespace(
            success=True,
            received_quantity=Decimal("30"),
            unit="kg",
            has_receipts=True,
            receipt_count=1,
        )
    )

    from app.modules.catering.services.catering_delivery_readiness import (
        CateringDeliveryReadinessService,
    )

    service = CateringDeliveryReadinessService(
        requirement_repository=requirement_repository,
        consumption_evidence_repository=consumption_evidence_repository,
        procurement_evidence_resolver=procurement_evidence_resolver,
    )

    return (
        event,
        service,
        requirement_repository,
        consumption_evidence_repository,
        procurement_evidence_resolver,
    )


def _requirement(
    *,
    fulfilment_type="INVENTORY",
    stock_item_id=2,
    quantity="30",
    unit="kg",
):
    return SimpleNamespace(
        id=9,
        event_id=6,
        stock_item_id=stock_item_id,
        quantity=Decimal(quantity) if quantity is not None else None,
        unit=unit,
        fulfilment_type=fulfilment_type,
        status="READY",
    )


def _evidence(
    *,
    quantity="30",
    unit="kg",
    movement_type="ISSUE",
    movement_quantity="-30",
    movement_status="POSTED",
    movement_stock_item_id=2,
    movement_unit="kg",
    is_deleted=False,
):
    movement = SimpleNamespace(
        movement_type=movement_type,
        quantity=Decimal(movement_quantity),
        status=movement_status,
        stock_item_id=movement_stock_item_id,
        unit=movement_unit,
        is_deleted=False,
    )
    return SimpleNamespace(
        quantity=Decimal(quantity),
        unit=unit,
        stock_movement=movement,
        is_deleted=is_deleted,
    )


# ---------------------------------------------------------------------------
# INVENTORY fulfilment — existing physical-consumption validation
# ---------------------------------------------------------------------------


def test_delivery_is_blocked_when_inventory_requirement_has_no_consumption():
    (
        event,
        service,
        requirement_repository,
        evidence_repository,
        procurement_resolver,
    ) = _build_service(_requirement(), [])

    with pytest.raises(EntityValidationException, match="consumption"):
        service.ensure_delivery_ready(event)

    requirement_repository.get_by_event_id.assert_called_once_with(event.id)
    evidence_repository.get_by_requirement_id.assert_called_once_with(9)
    procurement_resolver.get_receipt_status.assert_not_called()


def test_delivery_is_blocked_when_inventory_consumption_is_insufficient():
    event, service, *_ = _build_service(
        _requirement(),
        [_evidence(quantity="2", movement_quantity="-2")],
    )

    with pytest.raises(EntityValidationException, match="insufficient"):
        service.ensure_delivery_ready(event)


@pytest.mark.parametrize(
    "evidence, message",
    [
        (_evidence(movement_status="DRAFT"), "POSTED"),
        (_evidence(movement_type="RECEIPT", movement_quantity="30"), "ISSUE"),
        (_evidence(movement_quantity="30"), "negative"),
        (_evidence(movement_stock_item_id=99), "stock item"),
        (_evidence(movement_unit="pieces"), "unit"),
        (_evidence(unit="pieces"), "unit"),
        (_evidence(is_deleted=True), "Deleted"),
    ],
)
def test_delivery_is_blocked_for_invalid_inventory_consumption(evidence, message):
    event, service, *_ = _build_service(_requirement(), [evidence])

    with pytest.raises(EntityValidationException, match=message):
        service.ensure_delivery_ready(event)


def test_delivery_is_allowed_when_posted_inventory_issue_covers_requirement():
    event, service, *_ = _build_service(
        _requirement(),
        [_evidence(quantity="30", movement_quantity="-30")],
    )

    service.ensure_delivery_ready(event)


def test_delivery_is_blocked_when_inventory_evidence_has_no_stock_movement():
    evidence = _evidence()
    evidence.stock_movement = None
    event, service, *_ = _build_service(_requirement(), [evidence])

    with pytest.raises(EntityValidationException, match="posted stock movement"):
        service.ensure_delivery_ready(event)


@pytest.mark.parametrize(
    "requirement, message",
    [
        (
            _requirement(stock_item_id=None),
            "stock item and unit",
        ),
        (
            _requirement(quantity="0"),
            "quantities are invalid",
        ),
        (
            _requirement(quantity=None),
            "quantities are invalid",
        ),
    ],
)
def test_delivery_is_blocked_for_invalid_inventory_requirement_data(
    requirement,
    message,
):
    event, service, *_ = _build_service(requirement, [])

    with pytest.raises(EntityValidationException, match=message):
        service.ensure_delivery_ready(event)


# ---------------------------------------------------------------------------
# PROCUREMENT fulfilment — posted receipt evidence, without consumption
# ---------------------------------------------------------------------------


def test_delivery_is_allowed_when_procurement_receipts_cover_requirement():
    requirement = _requirement(fulfilment_type="PROCUREMENT")
    event, service, _, consumption_repository, resolver = _build_service(
        requirement,
    )

    service.ensure_delivery_ready(event)

    resolver.get_receipt_status.assert_called_once_with(requirement)
    consumption_repository.get_by_requirement_id.assert_not_called()


def test_delivery_is_blocked_when_procurement_receipts_are_insufficient():
    result = SimpleNamespace(
        success=True,
        received_quantity=Decimal("12"),
        unit="kg",
        has_receipts=True,
        receipt_count=1,
    )
    event, service, *_ = _build_service(
        _requirement(fulfilment_type="PROCUREMENT"),
        procurement_evidence=result,
    )

    with pytest.raises(EntityValidationException, match="insufficient"):
        service.ensure_delivery_ready(event)


def test_delivery_is_blocked_when_procurement_receipt_unit_does_not_match():
    result = SimpleNamespace(
        success=True,
        received_quantity=Decimal("30"),
        unit="pieces",
        has_receipts=True,
        receipt_count=1,
    )
    event, service, *_ = _build_service(
        _requirement(fulfilment_type="PROCUREMENT"),
        procurement_evidence=result,
    )

    with pytest.raises(EntityValidationException, match="unit"):
        service.ensure_delivery_ready(event)


def test_delivery_is_blocked_when_procurement_receipt_query_is_unavailable():
    result = SimpleNamespace(
        success=False,
        received_quantity=Decimal("30"),
        unit="kg",
        has_receipts=True,
        receipt_count=1,
        message="Inventory receipt query unavailable",
    )
    event, service, *_ = _build_service(
        _requirement(fulfilment_type="PROCUREMENT"),
        procurement_evidence=result,
    )

    with pytest.raises(EntityValidationException, match="unavailable"):
        service.ensure_delivery_ready(event)


def test_delivery_is_blocked_when_procurement_has_no_posted_receipts():
    result = SimpleNamespace(
        success=True,
        received_quantity=Decimal("0"),
        unit="kg",
        has_receipts=False,
        receipt_count=0,
    )
    event, service, *_ = _build_service(
        _requirement(fulfilment_type="PROCUREMENT"),
        procurement_evidence=result,
    )

    with pytest.raises(EntityValidationException, match="receipt"):
        service.ensure_delivery_ready(event)


def test_delivery_is_blocked_for_unknown_fulfilment_type():
    event, service, *_ = _build_service(
        _requirement(fulfilment_type="OTHER"),
    )

    with pytest.raises(EntityValidationException, match="fulfilment type"):
        service.ensure_delivery_ready(event)


def test_delivery_is_blocked_for_invalid_procurement_requirement_quantity():
    event, service, *_ = _build_service(
        _requirement(
            fulfilment_type="PROCUREMENT",
            quantity="0",
        ),
    )

    with pytest.raises(EntityValidationException, match="quantities are invalid"):
        service.ensure_delivery_ready(event)
