"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow command handlers.
"""

from __future__ import annotations

from app.core.execution.context import (
    ExecutionContext,
)
from app.core.execution.handlers.base import (
    BaseCommandHandler,
)
from app.core.execution.results import (
    ExecutionResult,
)
from app.modules.procurement.commands import (
    ApprovePurchaseOrderCommand,
    CancelPurchaseOrderCommand,
    RejectPurchaseOrderCommand,
    ReturnPurchaseOrderCommand,
    SubmitPurchaseOrderCommand,
)
from app.modules.procurement.services import (
    PurchaseOrderService,
)


class SubmitPurchaseOrderHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Order submission.
    """

    command_type = (
        SubmitPurchaseOrderCommand
    )

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseOrderService()
        )

    def handle(
        self,
        command: SubmitPurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Submit a Purchase Order through its workflow.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        previous_status = (
            purchase_order.status
        )

        try:
            self.service.submit(
                purchase_order
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in "
                    "DRAFT status before submission."
                ),
                error_code=(
                    "INVALID_PURCHASE_ORDER_STATE"
                ),
                data=purchase_order,
            )

        return ExecutionResult.success_result(
            data=purchase_order,
            message=(
                "Purchase Order submitted successfully."
            ),
            metadata={
                "purchase_order_id": (
                    purchase_order.id
                ),
                "previous_status": previous_status,
                "new_status": purchase_order.status,
                "operation": context.operation,
            },
        )


class ApprovePurchaseOrderHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Order approval.
    """

    command_type = (
        ApprovePurchaseOrderCommand
    )

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseOrderService()
        )

    def handle(
        self,
        command: ApprovePurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Approve a Purchase Order through its workflow.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        previous_status = (
            purchase_order.status
        )

        try:
            self.service.approve(
                purchase_order
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in "
                    "SUBMITTED status before approval."
                ),
                error_code=(
                    "INVALID_PURCHASE_ORDER_STATE"
                ),
                data=purchase_order,
            )

        return ExecutionResult.success_result(
            data=purchase_order,
            message=(
                "Purchase Order approved successfully."
            ),
            metadata={
                "purchase_order_id": (
                    purchase_order.id
                ),
                "previous_status": previous_status,
                "new_status": purchase_order.status,
                "operation": context.operation,
            },
        )


class RejectPurchaseOrderHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Order rejection.
    """

    command_type = (
        RejectPurchaseOrderCommand
    )

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseOrderService()
        )

    def handle(
        self,
        command: RejectPurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Reject a Purchase Order through its workflow.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        previous_status = (
            purchase_order.status
        )

        try:
            self.service.reject(
                purchase_order
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in "
                    "SUBMITTED status before rejection."
                ),
                error_code=(
                    "INVALID_PURCHASE_ORDER_STATE"
                ),
                data=purchase_order,
            )

        return ExecutionResult.success_result(
            data=purchase_order,
            message=(
                "Purchase Order rejected successfully."
            ),
            metadata={
                "purchase_order_id": (
                    purchase_order.id
                ),
                "previous_status": previous_status,
                "new_status": purchase_order.status,
                "operation": context.operation,
            },
        )


class ReturnPurchaseOrderHandler(
    BaseCommandHandler,
):
    """
    Handle returning a Purchase Order to draft.
    """

    command_type = (
        ReturnPurchaseOrderCommand
    )

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseOrderService()
        )

    def handle(
        self,
        command: ReturnPurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Return a Purchase Order to draft
        through its workflow.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        previous_status = (
            purchase_order.status
        )

        try:
            self.service.return_to_draft(
                purchase_order
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in "
                    "SUBMITTED status before return."
                ),
                error_code=(
                    "INVALID_PURCHASE_ORDER_STATE"
                ),
                data=purchase_order,
            )

        return ExecutionResult.success_result(
            data=purchase_order,
            message=(
                "Purchase Order returned to draft "
                "successfully."
            ),
            metadata={
                "purchase_order_id": (
                    purchase_order.id
                ),
                "previous_status": previous_status,
                "new_status": purchase_order.status,
                "operation": context.operation,
            },
        )


class CancelPurchaseOrderHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Order cancellation.
    """

    command_type = (
        CancelPurchaseOrderCommand
    )

    def __init__(
        self,
        service: PurchaseOrderService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseOrderService()
        )

    def handle(
        self,
        command: CancelPurchaseOrderCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Cancel an approved Purchase Order
        through its workflow.
        """

        purchase_order = self.service.get(
            command.purchase_order_id
        )

        previous_status = (
            purchase_order.status
        )

        try:
            self.service.cancel(
                purchase_order
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Order must be in "
                    "APPROVED status before cancellation."
                ),
                error_code=(
                    "INVALID_PURCHASE_ORDER_STATE"
                ),
                data=purchase_order,
            )

        return ExecutionResult.success_result(
            data=purchase_order,
            message=(
                "Purchase Order cancelled successfully."
            ),
            metadata={
                "purchase_order_id": (
                    purchase_order.id
                ),
                "previous_status": previous_status,
                "new_status": purchase_order.status,
                "operation": context.operation,
            },
        )


__all__ = [
    "ApprovePurchaseOrderHandler",
    "CancelPurchaseOrderHandler",
    "RejectPurchaseOrderHandler",
    "ReturnPurchaseOrderHandler",
    "SubmitPurchaseOrderHandler",
]
