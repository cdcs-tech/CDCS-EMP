"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration Contracts

Defines the domain-level contract used when Procurement communicates
a purchase-order receipt to Inventory.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


INVENTORY_INTEGRATION_PROVIDER = "inventory"

INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION = (
    "receive_purchase_order"
)


@dataclass(frozen=True, slots=True)
class PurchaseOrderReceiptRequest:
    """
    Domain contract for communicating a received Purchase Order line
    from Procurement to Inventory.

    This contract carries Procurement-owned business context only.
    Inventory remains authoritative for physical stock effects.
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

    notes: str | None = None

    def __post_init__(self) -> None:
        """
        Validate the minimum invariants required by the integration
        contract.
        """

        required_values = {
            "purchase_order_reference": (
                self.purchase_order_reference
            ),
            "purchase_order_line_reference": (
                self.purchase_order_line_reference
            ),
            "stock_item_reference": (
                self.stock_item_reference
            ),
            "inventory_location_reference": (
                self.inventory_location_reference
            ),
            "unit": self.unit,
            "receiving_reference": (
                self.receiving_reference
            ),
            "idempotency_key": self.idempotency_key,
        }

        for field_name, value in required_values.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} is required."
                )

        if not isinstance(
            self.quantity_received,
            Decimal,
        ):
            raise TypeError(
                "quantity_received must be a Decimal."
            )

        if self.quantity_received <= Decimal("0"):
            raise ValueError(
                "quantity_received must be greater than zero."
            )

        if not isinstance(self.received_at, datetime):
            raise TypeError(
                "received_at must be a datetime."
            )

        if self.notes is not None:
            if not isinstance(self.notes, str):
                raise TypeError(
                    "notes must be a string or None."
                )
