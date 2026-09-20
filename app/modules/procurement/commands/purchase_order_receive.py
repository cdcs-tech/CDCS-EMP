"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order receiving execution command.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.core.execution.commands.base import BaseCommand
from app.core.execution.commands.metadata import CommandMetadata
from app.core.execution.commands.types import CommandType


class ReceivePurchaseOrderCommand(BaseCommand):
    """
    Command to communicate a received Purchase Order line
    to the Inventory integration boundary.

    This is an integration execution operation, not a
    Purchase Order workflow transition.
    """

    command_name = "procurement.purchase_order.receive"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Receive Purchase Order",
        module_name="PROCUREMENT",
        operation="purchase_order.receive",
        version="1.0",
        description=(
            "Communicate a received Purchase Order line "
            "to the Inventory integration boundary."
        ),
        category="integration",
    )

    def __init__(
        self,
        purchase_order_id: int,
        purchase_order_reference: str,
        purchase_order_line_reference: str,
        stock_item_reference: str,
        inventory_location_reference: str,
        quantity_received: Decimal,
        unit: str,
        received_at: datetime,
        receiving_reference: str,
        idempotency_key: str,
        notes: str | None = None,
    ) -> None:
        self.purchase_order_id = purchase_order_id
        self.purchase_order_reference = purchase_order_reference
        self.purchase_order_line_reference = (
            purchase_order_line_reference
        )
        self.stock_item_reference = stock_item_reference
        self.inventory_location_reference = (
            inventory_location_reference
        )
        self.quantity_received = quantity_received
        self.unit = unit
        self.received_at = received_at
        self.receiving_reference = receiving_reference
        self.idempotency_key = idempotency_key
        self.notes = notes

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.purchase_order_id,
            int,
        ):
            raise ValueError(
                "purchase_order_id must be an integer."
            )

        if self.purchase_order_id <= 0:
            raise ValueError(
                "purchase_order_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name
