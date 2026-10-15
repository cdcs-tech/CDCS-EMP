"""Tests for Inventory-owned stock fulfilment contract types."""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from app.modules.catering.services.inventory_contracts import (
    InventoryAvailabilityResult,
    InventoryStockVerificationResult,
)


def test_inventory_availability_result_preserves_quantity_snapshot() -> None:
    result = InventoryAvailabilityResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        physical_quantity=Decimal("10.000"),
        reserved_quantity=Decimal("3.000"),
        available_quantity=Decimal("7.000"),
        verified=True,
    )

    assert result.physical_quantity == Decimal("10.000")
    assert result.reserved_quantity == Decimal("3.000")
    assert result.available_quantity == Decimal("7.000")
    assert result.verified is True
    assert result.reason is None


def test_inventory_availability_result_can_represent_failed_verification() -> None:
    result = InventoryAvailabilityResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        physical_quantity=Decimal("10.000"),
        reserved_quantity=Decimal("0.000"),
        available_quantity=Decimal("0.000"),
        verified=False,
        reason="Stock eligibility could not be verified.",
    )

    assert result.verified is False
    assert result.reason == "Stock eligibility could not be verified."


def test_inventory_availability_result_is_immutable() -> None:
    result = InventoryAvailabilityResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        physical_quantity=Decimal("10.000"),
        reserved_quantity=Decimal("3.000"),
        available_quantity=Decimal("7.000"),
        verified=True,
    )

    with pytest.raises(FrozenInstanceError):
        result.verified = False  # type: ignore[misc]


def test_stock_verification_result_preserves_approved_evidence_reference() -> None:
    result = InventoryStockVerificationResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        verified_quantity=Decimal("10.000"),
        verified=True,
        evidence_type="OPENING_STOCK",
        evidence_reference="VERIFY-1",
    )

    assert result.verified_quantity == Decimal("10.000")
    assert result.verified is True
    assert result.evidence_type == "OPENING_STOCK"
    assert result.evidence_reference == "VERIFY-1"
    assert result.reason is None


def test_stock_verification_result_can_represent_missing_evidence() -> None:
    result = InventoryStockVerificationResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        verified_quantity=Decimal("0.000"),
        verified=False,
        reason="No approved stock verification evidence was found.",
    )

    assert result.verified is False
    assert result.evidence_type is None
    assert result.evidence_reference is None
    assert result.reason == (
        "No approved stock verification evidence was found."
    )


def test_stock_verification_result_is_immutable() -> None:
    result = InventoryStockVerificationResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        verified_quantity=Decimal("10.000"),
        verified=True,
        evidence_type="INVENTORY_VERIFICATION",
        evidence_reference="VERIFY-2",
    )

    with pytest.raises(FrozenInstanceError):
        result.verified = False  # type: ignore[misc]
