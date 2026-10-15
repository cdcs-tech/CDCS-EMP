"""Inventory-owned contracts for Catering stock fulfilment.

These immutable result types define the boundary between Catering
requirements and Inventory-owned stock verification.

They are contracts only. They do not query the database, establish
stock provenance, reserve stock, or guarantee concurrency safety.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class InventoryAvailabilityResult:
    """Read-only snapshot of verified stock availability.

    A verified result represents an Inventory service decision for the
    specified stock item, location, and unit. It is not a reservation
    and must not be treated as a concurrency-safe allocation guarantee.
    """

    stock_item_id: int
    location_id: int
    unit: str
    physical_quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal
    verified: bool
    reason: str | None = None


@dataclass(frozen=True)
class InventoryStockVerificationResult:
    """Read-only outcome of existing-stock eligibility verification.

    Evidence references identify the Inventory-owned record supporting
    verification. The contract does not imply that such records already
    exist or that a movement type alone proves approval.
    """

    stock_item_id: int
    location_id: int
    unit: str
    verified_quantity: Decimal
    verified: bool
    evidence_type: str | None = None
    evidence_reference: str | None = None
    reason: str | None = None


__all__ = [
    "InventoryAvailabilityResult",
    "InventoryStockVerificationResult",
]
