"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order receiving execution handler.
"""

from __future__ import annotations

from decimal import Decimal

from app.core.execution.context import ExecutionContext
from app.core.execution.handlers.base import BaseCommandHandler
from app.core.execution.results import ExecutionResult
from app.core.integration import (
    IntegrationLifecycle,
    IntegrationRequest,
)
from app.modules.procurement.commands.purchase_order_receive import (
    ReceivePurchaseOrderCommand,
)
from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)
from app.modules.procurement.services import (
    PurchaseOrderLineService,
    PurchaseOrderService,
)


class ReceivePurchaseOrderHandler(BaseCommandHandler):
    """
    Validate and dispatch an approved Purchase Order receipt.

    Procurement validates the persisted Purchase Order and Purchase
    Order Line before constructing the Procurement-to-Inventory
    integration request. Inventory remains responsible for recording
    the physical stock movement.

    This handler does not modify Purchase Order workflow state or
    Inventory stock directly.
    """

    command_type = ReceivePurchaseOrderCommand

    _LINE_REFERENCE_PREFIX = "PO-LINE-"

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
        integration_lifecycle: IntegrationLifecycle | None = None,
        purchase_order_line_service: PurchaseOrderLineService | None = None,
    ) -> None:
        self.service = service or PurchaseOrderService()
        self.purchase_order_line_service = (
            purchase_order_line_service
            or PurchaseOrderLineService()
        )
        self.integration_lifecycle = (
            integration_lifecycle or IntegrationLifecycle()
        )

    def handle(
        self,
        command: ReceivePurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Validate the Purchase Order and line, then request receipt
        processing through the enterprise integration lifecycle.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        if purchase_order is None:
            return ExecutionResult.failure_result(
                message="Purchase Order does not exist.",
                error_code="PURCHASE_ORDER_NOT_FOUND",
            )

        if purchase_order.status != "APPROVED":
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in APPROVED status "
                    "before receiving."
                ),
                error_code="INVALID_PURCHASE_ORDER_STATE",
                data=purchase_order,
            )

        if (
            command.purchase_order_reference
            != purchase_order.reference
        ):
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order reference does not match "
                    "the persisted Purchase Order."
                ),
                error_code="PURCHASE_ORDER_REFERENCE_MISMATCH",
                data=purchase_order,
            )

        line_reference = command.purchase_order_line_reference

        if (
            not isinstance(line_reference, str)
            or not line_reference.startswith(
                self._LINE_REFERENCE_PREFIX
            )
        ):
            return ExecutionResult.failure_result(
                message="Purchase Order Line reference is invalid.",
                error_code="INVALID_PURCHASE_ORDER_LINE_REFERENCE",
                data=purchase_order,
            )

        line_guid = line_reference[
            len(self._LINE_REFERENCE_PREFIX):
        ].strip()

        if not line_guid:
            return ExecutionResult.failure_result(
                message="Purchase Order Line reference is invalid.",
                error_code="INVALID_PURCHASE_ORDER_LINE_REFERENCE",
                data=purchase_order,
            )

        purchase_order_line = (
            self.purchase_order_line_service.get_by_guid(
                line_guid
            )
        )

        if purchase_order_line is None:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order Line could not be found "
                    "using the supplied reference."
                ),
                error_code="PURCHASE_ORDER_LINE_NOT_FOUND",
                data=purchase_order,
            )

        if (
            purchase_order_line.purchase_order_id
            != purchase_order.id
        ):
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order Line does not belong "
                    "to the supplied Purchase Order."
                ),
                error_code="PURCHASE_ORDER_LINE_MISMATCH",
                data=purchase_order,
            )

        persisted_stock_item_reference = (
            purchase_order_line.stock_item_reference
        )

        if (
            not persisted_stock_item_reference
            or command.stock_item_reference
            != persisted_stock_item_reference
        ):
            return ExecutionResult.failure_result(
                message=(
                    "Stock item reference does not match "
                    "the Purchase Order Line."
                ),
                error_code=(
                    "PURCHASE_ORDER_LINE_STOCK_ITEM_MISMATCH"
                ),
                data=purchase_order,
            )

        if (
            not purchase_order_line.unit
            or command.unit != purchase_order_line.unit
        ):
            return ExecutionResult.failure_result(
                message=(
                    "Receipt unit does not match "
                    "the Purchase Order Line unit."
                ),
                error_code="PURCHASE_ORDER_LINE_UNIT_MISMATCH",
                data=purchase_order,
            )

        # Derive valuation only from persisted Procurement records.
        unit_price = purchase_order_line.unit_price
        currency = purchase_order.currency

        has_valid_valuation = (
            isinstance(unit_price, Decimal)
            and unit_price.is_finite()
            and unit_price >= Decimal("0")
            and isinstance(currency, str)
            and currency in {"USD", "SSP"}
        )

        valuation_unit_price = (
            unit_price if has_valid_valuation else None
        )
        valuation_currency = (
            currency if has_valid_valuation else None
        )
        valuation_price_basis = (
            "PO_LINE_UNIT_PRICE"
            if has_valid_valuation
            else None
        )

        try:
            receipt = PurchaseOrderReceiptRequest(
                purchase_order_reference=purchase_order.reference,
                purchase_order_line_reference=(
                    f"{self._LINE_REFERENCE_PREFIX}"
                    f"{purchase_order_line.guid}"
                ),
                stock_item_reference=(
                    persisted_stock_item_reference
                ),
                inventory_location_reference=(
                    command.inventory_location_reference
                ),
                quantity_received=command.quantity_received,
                unit=purchase_order_line.unit,
                received_at=command.received_at,
                receiving_reference=command.receiving_reference,
                idempotency_key=command.idempotency_key,
                valuation_unit_price=valuation_unit_price,
                valuation_currency=valuation_currency,
                valuation_price_basis=valuation_price_basis,
                notes=command.notes,
            )
        except (TypeError, ValueError) as exc:
            return ExecutionResult.failure_result(
                message=str(exc),
                error_code="INVALID_PURCHASE_ORDER_RECEIPT",
                data=purchase_order,
            )

        request = IntegrationRequest(
            provider=INVENTORY_INTEGRATION_PROVIDER,
            operation=(
                INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
            ),
            payload=receipt,
            metadata={
                "module": "PROCUREMENT",
                "purchase_order_id": purchase_order.id,
                "operation": context.operation,
                "subject": context.user_id,
            },
        )

        try:
            result = self.integration_lifecycle.execute(
                request,
                subject=context.user_id,
            )
        except Exception as exc:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order receiving integration "
                    "could not be executed."
                ),
                error_code=(
                    "PURCHASE_ORDER_RECEIPT_INTEGRATION_FAILED"
                ),
                data=purchase_order,
                metadata={
                    "purchase_order_id": purchase_order.id,
                    "operation": context.operation,
                    "error": str(exc),
                },
            )

        if result.failed:
            response = result.response

            return ExecutionResult.failure_result(
                message=(
                    response.message
                    if response is not None and response.message
                    else (
                        "Inventory rejected the "
                        "Purchase Order receipt."
                    )
                ),
                error_code="PURCHASE_ORDER_RECEIPT_REJECTED",
                data=result,
                metadata={
                    "purchase_order_id": purchase_order.id,
                    "operation": context.operation,
                    "provider": result.provider,
                    "integration_operation": result.operation,
                },
            )

        return ExecutionResult.success_result(
            data=result,
            message=(
                "Purchase Order receipt submitted "
                "to Inventory successfully."
            ),
            metadata={
                "purchase_order_id": purchase_order.id,
                "operation": context.operation,
                "provider": result.provider,
                "integration_operation": result.operation,
            },
        )
