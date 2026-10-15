
"""Inventory-owned stock availability service.

Returns a read-only snapshot of physical stock less active allocations.
This is not a reservation and does not provide concurrency protection.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import func

from app.extensions import db
from app.modules.catering.models import EventRequirementStockAllocation
from app.modules.catering.models.stock_balance import StockBalance
from app.modules.catering.repositories.balance import StockBalanceRepository
from app.modules.catering.repositories.stock_item import StockItemRepository
from app.modules.catering.services.inventory_contracts import (
    InventoryAvailabilityResult,
)


class InventoryAvailabilityService:
    """Calculate available stock from authoritative balance and allocation data."""

    ACTIVE_ALLOCATION_STATUS = "ACTIVE"
    QUANTITY_SCALE = Decimal("0.001")

    def __init__(
        self,
        *,
        balance_repository: Any | None = None,
        stock_item_repository: Any | None = None,
        allocation_query: Any | None = None,
    ) -> None:
        self._balance_repository = (
            balance_repository
            if balance_repository is not None
            else StockBalanceRepository()
        )
        self._stock_item_repository = (
            stock_item_repository
            if stock_item_repository is not None
            else StockItemRepository()
        )
        # Injectable for isolated tests. The default uses the current
        # SQLAlchemy session to query active allocations.
        self._allocation_query = allocation_query

    @classmethod
    def _quantity(cls, value: object, field: str) -> Decimal:
        """Parse a finite, non-negative quantity with at most 3 decimals."""
        try:
            quantity = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f"{field} is invalid.") from exc

        if not quantity.is_finite() or quantity < 0:
            raise ValueError(f"{field} must be finite and non-negative.")

        if quantity != quantity.quantize(cls.QUANTITY_SCALE):
            raise ValueError(f"{field} cannot exceed three decimal places.")

        return quantity

    @staticmethod
    def _positive_identifier(value: object, field: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{field} must be a positive integer.")
        return value

    @staticmethod
    def _required_unit(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required.")
        return value.strip().casefold()

    def _active_allocated_quantity(
        self,
        *,
        stock_item_id: int,
        location_id: int,
    ) -> Decimal:
        """Return active allocations for the specified item and location."""
        if self._allocation_query is not None:
            value = self._allocation_query(
                stock_item_id=stock_item_id,
                location_id=location_id,
                status=self.ACTIVE_ALLOCATION_STATUS,
            )
        else:
            value = (
                db.session.query(
                    func.coalesce(
                        func.sum(EventRequirementStockAllocation.quantity),
                        0,
                    )
                )
                .filter(
                    EventRequirementStockAllocation.stock_item_id
                    == stock_item_id,
                    EventRequirementStockAllocation.location_id == location_id,
                    EventRequirementStockAllocation.status
                    == self.ACTIVE_ALLOCATION_STATUS,
                )
                .scalar()
            )

        return self._quantity(value or 0, "Active allocation total")

    def _unverified(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        unit: str,
        reason: str,
        physical_quantity: Decimal = Decimal("0.000"),
        reserved_quantity: Decimal = Decimal("0.000"),
    ) -> InventoryAvailabilityResult:
        return InventoryAvailabilityResult(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=unit,
            physical_quantity=physical_quantity,
            reserved_quantity=reserved_quantity,
            available_quantity=Decimal("0.000"),
            verified=False,
            reason=reason,
        )

    def get_available_quantity(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        unit: str,
    ) -> InventoryAvailabilityResult:
        """Return physical stock less active allocations, failing closed."""
        stock_item_id = self._positive_identifier(
            stock_item_id,
            "stock_item_id",
        )
        location_id = self._positive_identifier(location_id, "location_id")
        normalized_unit = self._required_unit(unit, "Unit")

        stock_item = self._stock_item_repository.get_by_id(stock_item_id)
        if stock_item is None:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason="Stock Item does not exist.",
            )

        if getattr(stock_item, "is_active", True) is not True:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason="Stock Item is inactive.",
            )

        product = getattr(stock_item, "product", None)
        if product is None:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason="Stock Item has no associated Product.",
            )

        product_unit = getattr(product, "unit", None)
        if (
            not isinstance(product_unit, str)
            or not product_unit.strip()
            or product_unit.strip().casefold() != normalized_unit
        ):
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason="Requested unit does not match the Product unit.",
            )

        try:
            balance = (
                self._balance_repository.get_by_stock_item_and_location(
                    stock_item_id,
                    location_id,
                )
            )
        except Exception as exc:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason=f"Stock balance could not be verified: {exc}",
            )

        if balance is None:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason="No stock balance exists at the requested location.",
            )

        try:
            physical_quantity = self._quantity(
                getattr(balance, "quantity", None),
                "Physical stock quantity",
            )
            reserved_quantity = self._active_allocated_quantity(
                stock_item_id=stock_item_id,
                location_id=location_id,
            )
        except Exception as exc:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason=f"Stock availability could not be verified: {exc}",
            )

        if reserved_quantity > physical_quantity:
            return self._unverified(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=normalized_unit,
                reason="Active allocations exceed the physical stock balance.",
                physical_quantity=physical_quantity,
                reserved_quantity=reserved_quantity,
            )

        return InventoryAvailabilityResult(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=normalized_unit,
            physical_quantity=physical_quantity,
            reserved_quantity=reserved_quantity,
            available_quantity=physical_quantity - reserved_quantity,
            verified=True,
        )


__all__ = ["InventoryAvailabilityService"]
