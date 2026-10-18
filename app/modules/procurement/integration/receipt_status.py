"""Procurement-side Purchase Order Line receipt-status derivation."""

from dataclasses import dataclass
from decimal import Decimal

from app.modules.procurement.integration.contracts import (
    InventoryReceiptStatusQueryResult,
)


NOT_RECEIVED = "NOT_RECEIVED"
PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
FULLY_RECEIVED = "FULLY_RECEIVED"
OVER_RECEIVED = "OVER_RECEIVED"
STATUS_UNAVAILABLE = "STATUS_UNAVAILABLE"


@dataclass(frozen=True)
class PurchaseOrderLineReceiptStatus:
    """Derived receiving status for one Purchase Order Line."""

    status: str
    ordered_quantity: Decimal | None
    received_quantity: Decimal | None
    unit: str | None
    receipt_count: int | None
    error_code: str | None = None


def _unavailable(
    ordered_quantity: Decimal | None,
    error_code: str,
) -> PurchaseOrderLineReceiptStatus:
    """Return an unavailable result without presenting uncertain facts."""
    return PurchaseOrderLineReceiptStatus(
        status=STATUS_UNAVAILABLE,
        ordered_quantity=ordered_quantity,
        received_quantity=None,
        unit=None,
        receipt_count=None,
        error_code=error_code,
    )


def derive_purchase_order_line_receipt_status(
    *,
    purchase_order_reference: str,
    purchase_order_line_reference: str,
    ordered_quantity: Decimal,
    ordered_unit: str,
    inventory_result: InventoryReceiptStatusQueryResult,
) -> PurchaseOrderLineReceiptStatus:
    """Derive status from authoritative Inventory receipt facts.

    Unit matching permits trimming surrounding whitespace only. No unit
    conversion, case folding, or floating-point tolerance is applied.
    """
    valid_ordered_quantity = (
        isinstance(ordered_quantity, Decimal)
        and ordered_quantity.is_finite()
        and ordered_quantity > Decimal("0")
    )

    if not valid_ordered_quantity:
        return _unavailable(None, "INVALID_ORDERED_QUANTITY")

    if (
        not isinstance(ordered_unit, str)
        or not ordered_unit.strip()
    ):
        return _unavailable(
            ordered_quantity,
            "ORDERED_UNIT_UNAVAILABLE",
        )

    if not isinstance(inventory_result, InventoryReceiptStatusQueryResult):
        return _unavailable(
            ordered_quantity,
            "INVALID_INVENTORY_RESULT",
        )

    if inventory_result.success is not True:
        return _unavailable(
            ordered_quantity,
            inventory_result.error_code or "QUERY_FAILED",
        )

    if (
        inventory_result.purchase_order_reference
        != purchase_order_reference
        or inventory_result.purchase_order_line_reference
        != purchase_order_line_reference
    ):
        return _unavailable(
            ordered_quantity,
            "RECEIPT_REFERENCE_MISMATCH",
        )

    received_quantity = inventory_result.received_quantity
    inventory_unit = inventory_result.unit
    receipt_count = inventory_result.receipt_count
    has_receipts = inventory_result.has_receipts

    if (
        not isinstance(received_quantity, Decimal)
        or not received_quantity.is_finite()
        or received_quantity < Decimal("0")
    ):
        return _unavailable(
            ordered_quantity,
            "INVALID_RECEIVED_QUANTITY",
        )

    if (
        not isinstance(inventory_unit, str)
        or not inventory_unit.strip()
        or inventory_unit.strip() != ordered_unit.strip()
    ):
        return _unavailable(
            ordered_quantity,
            "INCOMPATIBLE_UNITS",
        )

    if (
        isinstance(receipt_count, bool)
        or not isinstance(receipt_count, int)
        or receipt_count < 0
        or not isinstance(has_receipts, bool)
    ):
        return _unavailable(
            ordered_quantity,
            "INCONSISTENT_RECEIPT_HISTORY",
        )

    history_is_consistent = (
        (
            received_quantity == Decimal("0")
            and receipt_count == 0
            and has_receipts is False
        )
        or (
            received_quantity > Decimal("0")
            and receipt_count > 0
            and has_receipts is True
        )
    )

    if not history_is_consistent:
        return _unavailable(
            ordered_quantity,
            "INCONSISTENT_RECEIPT_HISTORY",
        )

    if received_quantity == Decimal("0"):
        status = NOT_RECEIVED
    elif received_quantity < ordered_quantity:
        status = PARTIALLY_RECEIVED
    elif received_quantity == ordered_quantity:
        status = FULLY_RECEIVED
    else:
        status = OVER_RECEIVED

    return PurchaseOrderLineReceiptStatus(
        status=status,
        ordered_quantity=ordered_quantity,
        received_quantity=received_quantity,
        unit=ordered_unit.strip(),
        receipt_count=receipt_count,
    )


__all__ = [
    "FULLY_RECEIVED",
    "NOT_RECEIVED",
    "OVER_RECEIVED",
    "PARTIALLY_RECEIVED",
    "STATUS_UNAVAILABLE",
    "PurchaseOrderLineReceiptStatus",
    "derive_purchase_order_line_receipt_status",
]
