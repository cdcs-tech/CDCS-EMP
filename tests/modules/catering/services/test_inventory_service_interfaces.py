"""Tests for the Inventory service interface contracts."""

from decimal import Decimal

from app.modules.catering.services.inventory_contracts import (
    InventoryAvailabilityResult,
    InventoryStockVerificationResult,
)
from app.modules.catering.services.inventory_service_interfaces import (
    ExistingStockVerificationService,
    InventoryAvailabilityService,
)


class FakeInventoryAvailabilityService:
    """In-memory implementation of the availability protocol."""

    def get_available_quantity(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        unit: str,
    ) -> InventoryAvailabilityResult:
        return InventoryAvailabilityResult(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=unit,
            physical_quantity=Decimal("10.000"),
            reserved_quantity=Decimal("3.000"),
            available_quantity=Decimal("7.000"),
            verified=True,
        )


class FakeExistingStockVerificationService:
    """In-memory implementation of the stock verification protocol."""

    def verify_stock_eligibility(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
    ) -> InventoryStockVerificationResult:
        return InventoryStockVerificationResult(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=unit,
            verified_quantity=quantity,
            verified=True,
            evidence_type="INVENTORY_VERIFICATION",
            evidence_reference="VERIFY-TEST-1",
        )


def test_availability_implementation_conforms_to_protocol() -> None:
    service = FakeInventoryAvailabilityService()

    assert isinstance(service, InventoryAvailabilityService)

    result = service.get_available_quantity(
        stock_item_id=1,
        location_id=2,
        unit="kg",
    )

    assert isinstance(result, InventoryAvailabilityResult)
    assert result.stock_item_id == 1
    assert result.location_id == 2
    assert result.available_quantity == Decimal("7.000")
    assert result.verified is True


def test_stock_verification_implementation_conforms_to_protocol() -> None:
    service = FakeExistingStockVerificationService()

    assert isinstance(service, ExistingStockVerificationService)

    result = service.verify_stock_eligibility(
        stock_item_id=1,
        location_id=2,
        quantity=Decimal("5.000"),
        unit="kg",
    )

    assert isinstance(result, InventoryStockVerificationResult)
    assert result.verified_quantity == Decimal("5.000")
    assert result.verified is True
    assert result.evidence_type == "INVENTORY_VERIFICATION"
    assert result.evidence_reference == "VERIFY-TEST-1"


def test_unverified_results_remain_explicitly_unverified() -> None:
    availability = InventoryAvailabilityResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        physical_quantity=Decimal("0.000"),
        reserved_quantity=Decimal("0.000"),
        available_quantity=Decimal("0.000"),
        verified=False,
        reason="Availability could not be verified.",
    )
    verification = InventoryStockVerificationResult(
        stock_item_id=1,
        location_id=2,
        unit="kg",
        verified_quantity=Decimal("0.000"),
        verified=False,
        reason="Approved evidence was not found.",
    )

    assert availability.verified is False
    assert verification.verified is False
    assert availability.reason is not None
    assert verification.reason is not None
