"""Interfaces for Inventory-owned stock verification services.

These protocols define the boundary consumed by Catering. They contain
no database access or stock mutation logic.

Availability snapshots are not reservations. A concrete implementation
must not claim that an availability check protects against concurrent
allocations. Reservation safety belongs to a separate transactional
operation.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.modules.catering.services.inventory_contracts import (
    InventoryAvailabilityResult,
    InventoryStockVerificationResult,
)


@runtime_checkable
class InventoryAvailabilityService(Protocol):
    """Inventory-owned interface for querying stock availability."""

    def get_available_quantity(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        unit: str,
    ) -> InventoryAvailabilityResult:
        """Return an availability snapshot for the specified stock.

        Concrete implementations must fail closed when current
        availability cannot be established reliably.
        """
        ...


@runtime_checkable
class ExistingStockVerificationService(Protocol):
    """Inventory-owned interface for verifying existing-stock evidence."""

    def verify_stock_eligibility(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
    ) -> InventoryStockVerificationResult:
        """Verify that the requested quantity has acceptable evidence.

        Concrete implementations must not infer approval from a movement
        type alone. Missing or invalid evidence must not yield a
        successful verification result.
        """
        ...


__all__ = [
    "ExistingStockVerificationService",
    "InventoryAvailabilityService",
]
