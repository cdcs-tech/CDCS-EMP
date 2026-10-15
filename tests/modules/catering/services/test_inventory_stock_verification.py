"""Tests for existing-stock verification using an in-memory evidence provider."""

from dataclasses import dataclass
from decimal import Decimal

import pytest

from app.modules.catering.services.inventory_contracts import (
    InventoryStockVerificationResult,
)
from app.modules.catering.services.inventory_stock_verification import (
    InventoryStockVerificationService,
)


@dataclass
class FakeStockEvidence:
    stock_item_id: int = 1
    location_id: int = 2
    unit: str = "kg"
    verified_quantity: Decimal = Decimal("10.000")
    status: str = "APPROVED"
    evidence_type: str = "INVENTORY_VERIFICATION"
    reference: str = "VERIFY-TEST-1"


class FakeEvidenceProvider:
    def __init__(self, evidence=None):
        self.evidence = evidence
        self.calls = []

    def get_approved_stock_evidence(self, *, stock_item_id, location_id):
        self.calls.append((stock_item_id, location_id))
        return self.evidence


def make_service(evidence=None):
    provider = FakeEvidenceProvider(evidence)
    return InventoryStockVerificationService(evidence_provider=provider), provider


def test_approved_evidence_verifies_requested_quantity():
    service, provider = make_service(FakeStockEvidence())

    result = service.verify_stock_eligibility(
        stock_item_id=1,
        location_id=2,
        quantity=Decimal("5.000"),
        unit="KG",
    )

    assert isinstance(result, InventoryStockVerificationResult)
    assert result.verified is True
    assert result.verified_quantity == Decimal("10.000")
    assert result.unit == "kg"
    assert result.evidence_type == "INVENTORY_VERIFICATION"
    assert result.evidence_reference == "VERIFY-TEST-1"
    assert provider.calls == [(1, 2)]


def test_missing_evidence_fails_closed():
    service, _ = make_service()

    result = service.verify_stock_eligibility(
        stock_item_id=1,
        location_id=2,
        quantity=Decimal("1.000"),
        unit="kg",
    )

    assert result.verified is False
    assert result.evidence_reference is None
    assert "No approved" in result.reason


@pytest.mark.parametrize(
    "changes, expected_reason",
    [
        ({"status": "PENDING"}, "not approved"),
        ({"evidence_type": "OPENING_BALANCE"}, "type is not eligible"),
        ({"stock_item_id": 99}, "different Stock Item"),
        ({"location_id": 99}, "different location"),
        ({"unit": "litre"}, "different unit"),
        ({"verified_quantity": Decimal("2.000")}, "does not cover"),
        ({"reference": ""}, "Evidence reference"),
        ({"verified_quantity": Decimal("1.0001")}, "three decimal places"),
    ],
)
def test_invalid_or_mismatched_evidence_fails_closed(changes, expected_reason):
    evidence = FakeStockEvidence()
    for field, value in changes.items():
        setattr(evidence, field, value)

    service, _ = make_service(evidence)

    result = service.verify_stock_eligibility(
        stock_item_id=1,
        location_id=2,
        quantity=Decimal("5.000"),
        unit="kg",
    )

    assert result.verified is False
    assert expected_reason.casefold() in result.reason.casefold()


@pytest.mark.parametrize(
    "quantity",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        Decimal("1.0001"),
    ],
)
def test_invalid_requested_quantity_is_rejected(quantity):
    service, _ = make_service(FakeStockEvidence())

    with pytest.raises(ValueError):
        service.verify_stock_eligibility(
            stock_item_id=1,
            location_id=2,
            quantity=quantity,
            unit="kg",
        )


@pytest.mark.parametrize(
    "stock_item_id, location_id, unit",
    [
        (0, 2, "kg"),
        (1, 0, "kg"),
        (True, 2, "kg"),
        (1, 2, " "),
    ],
)
def test_invalid_identifiers_or_unit_are_rejected(stock_item_id, location_id, unit):
    service, _ = make_service(FakeStockEvidence())

    with pytest.raises(ValueError):
        service.verify_stock_eligibility(
            stock_item_id=stock_item_id,
            location_id=location_id,
            quantity=Decimal("1.000"),
            unit=unit,
        )


def test_opening_balance_movement_type_alone_is_not_evidence():
    service, _ = make_service(
        FakeStockEvidence(evidence_type="OPENING_BALANCE")
    )

    result = service.verify_stock_eligibility(
        stock_item_id=1,
        location_id=2,
        quantity=Decimal("1.000"),
        unit="kg",
    )

    assert result.verified is False
    assert "type is not eligible" in result.reason

