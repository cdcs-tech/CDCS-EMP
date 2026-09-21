"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order receiving execution handler.
"""

from __future__ import annotations

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
from app.modules.procurement.services import PurchaseOrderService


class ReceivePurchaseOrderHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Order receiving communication.

    This handler does not modify the Purchase Order workflow
    or Inventory state directly. It constructs the approved
    Procurement ↔ Inventory contract and delegates delivery
    to the enterprise IntegrationLifecycle.
    """

    command_type = ReceivePurchaseOrderCommand

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
        integration_lifecycle: IntegrationLifecycle | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseOrderService()
        )
        self.integration_lifecycle = (
            integration_lifecycle
            or IntegrationLifecycle()
        )

    def handle(
        self,
        command: ReceivePurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Communicate a received Purchase Order line
        to the Inventory integration boundary.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        if purchase_order.status != "APPROVED":
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in "
                    "APPROVED status before receiving."
                ),
                error_code=(
                    "INVALID_PURCHASE_ORDER_STATE"
                ),
                data=purchase_order,
            )

        try:
            receipt = PurchaseOrderReceiptRequest(
                purchase_order_reference=(
                    command.purchase_order_reference
                ),
                purchase_order_line_reference=(
                    command.purchase_order_line_reference
                ),
                stock_item_reference=(
                    command.stock_item_reference
                ),
                inventory_location_reference=(
                    command.inventory_location_reference
                ),
                quantity_received=(
                    command.quantity_received
                ),
                unit=command.unit,
                received_at=command.received_at,
                receiving_reference=(
                    command.receiving_reference
                ),
                idempotency_key=(
                    command.idempotency_key
                ),
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
                error_code="PURCHASE_ORDER_RECEIPT_INTEGRATION_FAILED",
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
                    if response is not None
                    and response.message
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
