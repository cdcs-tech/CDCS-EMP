"""Verify inventory fulfilment for Catering Event Requirements."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from app.extensions import db
from app.modules.catering.models import EventRequirementStockAllocation
from app.modules.catering.services.inventory_availability import (
    InventoryAvailabilityService,
)


class EventRequirementFulfilmentVerifier:
    """Verify allocation coverage and current Inventory availability.

    Active allocations must exactly cover the requirement. Inventory must
    independently confirm that each allocated stock item and location has
    a verifiable balance and that active allocations are supported by
    physical stock and reported reservations.

    Availability checks are snapshots, not concurrency-safe reservations,
    and do not establish Purchase Order receipt provenance.
    """

    ACTIVE_ALLOCATION_STATUS = "ACTIVE"
    QUANTITY_SCALE = Decimal("0.001")

    def __init__(self, *, availability_service: Any | None = None) -> None:
        self._availability_service = (
            availability_service
            if availability_service is not None
            else InventoryAvailabilityService()
        )

    @classmethod
    def _quantity(cls, value: object, field: str) -> Decimal:
        """Return a finite positive quantity with at most three decimals."""
        try:
            quantity = Decimal(str(value))
            if not quantity.is_finite() or quantity <= 0:
                raise RuntimeError(
                    f"Event requirement {field} must be positive."
                )

            if quantity != quantity.quantize(cls.QUANTITY_SCALE):
                raise RuntimeError(
                    f"Event requirement {field} cannot exceed three "
                    "decimal places."
                )

        except (InvalidOperation, TypeError, ValueError) as exc:
            raise RuntimeError(
                f"Event requirement {field} is invalid."
            ) from exc

        return quantity

    @staticmethod
    def _normalize_unit(value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(
                "Event requirement or allocation unit is missing."
            )
        return value.strip().casefold()

    def _verify_allocation_availability(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        unit: str,
        allocated_quantity: Decimal,
    ) -> None:
        """Fail closed unless Inventory verifies sufficient physical support."""
        try:
            result = self._availability_service.get_available_quantity(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=unit,
            )
        except Exception as exc:
            raise RuntimeError(
                "Inventory availability could not be verified."
            ) from exc

        if result is None or getattr(result, "verified", False) is not True:
            reason = (
                getattr(result, "reason", None)
                if result is not None
                else None
            )
            detail = f" Reason: {reason}" if reason else ""
            raise RuntimeError(
                "Inventory availability is unverified for an active "
                f"allocation.{detail}"
            )

        if (
            getattr(result, "stock_item_id", None) != stock_item_id
            or getattr(result, "location_id", None) != location_id
        ):
            raise RuntimeError(
                "Inventory availability result does not match the "
                "active allocation's Stock Item and location."
            )

        result_unit = self._normalize_unit(getattr(result, "unit", None))
        if result_unit != unit:
            raise RuntimeError(
                "Inventory availability result uses a different unit "
                "from the active allocation."
            )

        try:
            physical_quantity = Decimal(
                str(getattr(result, "physical_quantity", None))
            )
            reserved_quantity = Decimal(
                str(getattr(result, "reserved_quantity", None))
            )
            available_quantity = Decimal(
                str(getattr(result, "available_quantity", None))
            )
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise RuntimeError(
                "Inventory availability quantities are invalid."
            ) from exc

        quantities = (
            physical_quantity,
            reserved_quantity,
            available_quantity,
        )
        if any(not value.is_finite() or value < 0 for value in quantities):
            raise RuntimeError(
                "Inventory availability quantities must be finite and "
                "non-negative."
            )

        if any(
            value != value.quantize(self.QUANTITY_SCALE)
            for value in quantities
        ):
            raise RuntimeError(
                "Inventory availability quantities cannot exceed three "
                "decimal places."
            )

        if physical_quantity - reserved_quantity != available_quantity:
            raise RuntimeError(
                "Inventory availability quantities are inconsistent."
            )

        if reserved_quantity > physical_quantity:
            raise RuntimeError(
                "Active allocations exceed the physical stock balance."
            )

        if allocated_quantity > physical_quantity:
            raise RuntimeError(
                "The allocation exceeds the physical stock balance at "
                "its location."
            )

        if reserved_quantity < allocated_quantity:
            raise RuntimeError(
                "Inventory reserved quantity does not cover the "
                "active allocation group."
            )


    def ensure_fulfilled(self, requirement: object) -> None:
        """Raise RuntimeError unless allocations and Inventory are verified."""
        requirement_id = getattr(requirement, "id", None)
        if requirement_id is None:
            raise RuntimeError(
                "Event requirement fulfilment cannot be verified without "
                "a persisted requirement."
            )

        stock_item_id = getattr(requirement, "stock_item_id", None)
        if stock_item_id is None:
            raise RuntimeError(
                "Event requirement fulfilment cannot be verified without "
                "a mapped Stock Item."
            )

        required_quantity = self._quantity(
            getattr(requirement, "quantity", None),
            "quantity",
        )
        required_unit = self._normalize_unit(
            getattr(requirement, "unit", None),
        )

        allocations = (
            db.session.query(EventRequirementStockAllocation)
            .filter(
                EventRequirementStockAllocation.event_requirement_id
                == requirement_id,
                EventRequirementStockAllocation.status
                == self.ACTIVE_ALLOCATION_STATUS,
            )
            .all()
        )

        if not allocations:
            raise RuntimeError(
                "Event requirement has no active inventory allocations."
            )

        allocated_quantity = Decimal("0")
        allocation_groups: dict[tuple[int, int], Decimal] = {}

        for allocation in allocations:
            if allocation.event_requirement_id != requirement_id:
                raise RuntimeError(
                    "An allocation belongs to a different Event Requirement."
                )

            if allocation.status != self.ACTIVE_ALLOCATION_STATUS:
                raise RuntimeError(
                    "A returned allocation is not in ACTIVE status."
                )

            if allocation.stock_item_id != stock_item_id:
                raise RuntimeError(
                    "An active allocation uses a different Stock Item "
                    "from the Event Requirement."
                )

            allocation_unit = self._normalize_unit(allocation.unit)
            if allocation_unit != required_unit:
                raise RuntimeError(
                    "An active allocation uses a different unit from "
                    "the Event Requirement."
                )

            location_id = getattr(allocation, "location_id", None)
            if (
                isinstance(location_id, bool)
                or not isinstance(location_id, int)
                or location_id <= 0
            ):
                raise RuntimeError(
                    "An active allocation has no valid inventory location."
                )

            quantity = self._quantity(
                allocation.quantity,
                "allocation quantity",
            )
            allocated_quantity += quantity

            allocation_key = (stock_item_id, location_id)
            allocation_groups[allocation_key] = (
                allocation_groups.get(allocation_key, Decimal("0"))
                + quantity
            )

        # Validate total allocation coverage before querying Inventory.
        if allocated_quantity < required_quantity:
            raise RuntimeError(
                "Event requirement is not fully fulfilled by active "
                f"inventory allocations: {allocated_quantity} "
                f"of {required_quantity} {required_unit} allocated."
            )

        if allocated_quantity > required_quantity:
            raise RuntimeError(
                "Active inventory allocations exceed the Event "
                f"Requirement quantity: {allocated_quantity} "
                f"allocated for {required_quantity} {required_unit} required."
            )

        # Verify each completed item/location group after domain validation.
        for (
            group_stock_item_id,
            group_location_id,
        ), group_quantity in allocation_groups.items():
            self._verify_allocation_availability(
                stock_item_id=group_stock_item_id,
                location_id=group_location_id,
                unit=required_unit,
                allocated_quantity=group_quantity,
            )


__all__ = [
    "EventRequirementFulfilmentVerifier",
]
