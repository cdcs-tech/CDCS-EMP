"""Procurement integration contracts.

This module contains explicit, immutable contracts owned by Procurement for
communication with other enterprise capabilities.

The contracts intentionally describe Procurement business facts only.
Downstream capabilities remain responsible for their own domain semantics,
persistence, and processing.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


# ---------------------------------------------------------------------------
# Inventory integration contract identities
# ---------------------------------------------------------------------------

INVENTORY_INTEGRATION_PROVIDER = "inventory"
INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION = "receive_purchase_order"


# ---------------------------------------------------------------------------
# Finance integration contract identities
# ---------------------------------------------------------------------------

FINANCE_INTEGRATION_PROVIDER = "finance"
FINANCE_PROCUREMENT_COMMITMENT_OPERATION = "procurement_commitment"


# ---------------------------------------------------------------------------
# Inventory integration payload
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PurchaseOrderReceiptRequest:
    """Procurement-owned request describing an actual purchase-order receipt.

    Inventory remains authoritative for physical stock effects. This
    contract communicates the Procurement-side receiving fact through the
    enterprise Integration Framework.
    """

    purchase_order_reference: str
    purchase_order_line_reference: str
    stock_item_reference: str
    inventory_location_reference: str
    quantity_received: Decimal
    unit: str
    received_at: datetime
    receiving_reference: str
    idempotency_key: str
    # Optional valuation evidence from the persisted approved PO line.
    # Missing evidence is permitted for a physical receipt but cannot
    # qualify that receipt as valued.
    valuation_unit_price: Decimal | None = None
    valuation_currency: str | None = None
    valuation_price_basis: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        required_strings = (
            self.purchase_order_reference,
            self.purchase_order_line_reference,
            self.stock_item_reference,
            self.inventory_location_reference,
            self.unit,
            self.receiving_reference,
            self.idempotency_key,
        )

        if any(not isinstance(value, str) or not value.strip()
               for value in required_strings):
            raise ValueError(
                "Purchase order receipt required string fields "
                "must be non-empty."
            )

        if not isinstance(self.quantity_received, Decimal):
            raise TypeError("quantity_received must be a Decimal.")

        if self.quantity_received <= Decimal("0"):
            raise ValueError("quantity_received must be greater than zero.")

        if not isinstance(self.received_at, datetime):
            raise TypeError("received_at must be a datetime.")

        if self.notes is not None and not isinstance(self.notes, str):
            raise TypeError("notes must be a string or None.")

        valuation_values = (
            self.valuation_unit_price,
            self.valuation_currency,
            self.valuation_price_basis,
        )

        if all(value is None for value in valuation_values):
            return

        if any(value is None for value in valuation_values):
            raise ValueError(
                "Receipt valuation evidence must be complete or entirely absent."
            )

        if not isinstance(self.valuation_unit_price, Decimal):
            raise TypeError("valuation_unit_price must be a Decimal or None.")

        if self.valuation_unit_price < Decimal("0"):
            raise ValueError("valuation_unit_price must not be negative.")

        if self.valuation_currency not in {"USD", "SSP"}:
            raise ValueError("valuation_currency must be USD or SSP.")

        if self.valuation_price_basis != "PO_LINE_UNIT_PRICE":
            raise ValueError(
                "valuation_price_basis must be PO_LINE_UNIT_PRICE."
            )

from dataclasses import dataclass
from decimal import Decimal


INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION = (
    "query_purchase_order_line_receipt_status"
)


@dataclass(frozen=True)
class PurchaseOrderLineReceiptStatusRequest:
    """Request authoritative Inventory receipt facts for one PO line."""

    purchase_order_reference: str
    purchase_order_line_reference: str
    stock_item_reference: str


@dataclass(frozen=True)
class InventoryReceiptStatusQueryResult:
    """Result of querying Inventory receipt history for one PO line.

    A failed or unavailable result must never be interpreted as zero receipts.
    """

    success: bool
    purchase_order_reference: str
    purchase_order_line_reference: str
    received_quantity: Decimal | None
    unit: str | None
    receipt_count: int | None
    has_receipts: bool | None
    error_code: str | None = None
    message: str | None = None


# ---------------------------------------------------------------------------
# Finance integration payload
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProcurementFinancialEffectLine:
    """Procurement-owned purchase-order line information for Finance.

    The line describes commercial procurement facts. It deliberately does
    not contain accounting instructions, ledger accounts, journal entries,
    payment information, tax treatment, or financial posting instructions.
    """

    purchase_order_line_reference: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    line_amount: Decimal

    def __post_init__(self) -> None:
        required_strings = (
            self.purchase_order_line_reference,
            self.description,
            self.unit,
        )

        if any(not isinstance(value, str) or not value.strip()
               for value in required_strings):
            raise ValueError(
                "Procurement financial-effect line required string fields "
                "must be non-empty."
            )

        if not isinstance(self.quantity, Decimal):
            raise TypeError("quantity must be a Decimal.")

        if self.quantity <= Decimal("0"):
            raise ValueError("quantity must be greater than zero.")

        if not isinstance(self.unit_price, Decimal):
            raise TypeError("unit_price must be a Decimal.")

        if self.unit_price < Decimal("0"):
            raise ValueError("unit_price must not be negative.")

        if not isinstance(self.line_amount, Decimal):
            raise TypeError("line_amount must be a Decimal.")

        if self.line_amount < Decimal("0"):
            raise ValueError("line_amount must not be negative.")


@dataclass(frozen=True, slots=True)
class ProcurementFinancialEffectRequest:
    """Procurement-owned business fact communicated to Finance.

    The successful Procurement transition of a Purchase Order to APPROVED
    creates the Procurement business fact eligible for Finance communication.

    This contract communicates procurement facts only. Finance determines
    financial treatment and remains authoritative for accounting records,
    invoices, payments, settlement, and ledger information.
    """

    purchase_order_reference: str
    purchase_request_reference: str
    supplier_reference: str
    purchase_order_date: datetime
    approved_at: datetime
    currency: str
    total_procurement_value: Decimal
    purchase_order_lines: tuple[ProcurementFinancialEffectLine, ...]
    idempotency_key: str

    def __post_init__(self) -> None:
        required_strings = (
            self.purchase_order_reference,
            self.purchase_request_reference,
            self.supplier_reference,
            self.currency,
            self.idempotency_key,
        )

        if any(not isinstance(value, str) or not value.strip()
               for value in required_strings):
            raise ValueError(
                "Procurement financial-effect required string fields "
                "must be non-empty."
            )

        if not isinstance(self.purchase_order_date, datetime):
            raise TypeError("purchase_order_date must be a datetime.")

        if not isinstance(self.approved_at, datetime):
            raise TypeError("approved_at must be a datetime.")

        if not isinstance(self.currency, str):
            raise TypeError("currency must be a string.")

        if not isinstance(self.total_procurement_value, Decimal):
            raise TypeError("total_procurement_value must be a Decimal.")

        if self.total_procurement_value < Decimal("0"):
            raise ValueError(
                "total_procurement_value must not be negative."
            )

        if not isinstance(self.purchase_order_lines, tuple):
            raise TypeError("purchase_order_lines must be a tuple.")

        if not self.purchase_order_lines:
            raise ValueError("purchase_order_lines must not be empty.")

        if any(
            not isinstance(line, ProcurementFinancialEffectLine)
            for line in self.purchase_order_lines
        ):
            raise TypeError(
                "purchase_order_lines must contain only "
                "ProcurementFinancialEffectLine instances."
            )

        if not isinstance(self.idempotency_key, str):
            raise TypeError("idempotency_key must be a string.")
