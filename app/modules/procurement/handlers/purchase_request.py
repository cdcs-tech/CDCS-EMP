"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Request workflow command handlers.
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
    ApprovePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
)

from app.modules.procurement.services import (
    PurchaseRequestService,
)


class SubmitPurchaseRequestHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Request submission.
    """

    command_type = (
        SubmitPurchaseRequestCommand
    )

    def __init__(
        self,
        service: PurchaseRequestService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseRequestService()
        )

    def handle(
        self,
        command: SubmitPurchaseRequestCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Submit a Purchase Request from DRAFT to SUBMITTED.
        """

        purchase_request = self.service.get(
            command.purchase_request_id
        )

        if purchase_request.status != "DRAFT":
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Request must be in "
                    "DRAFT status before submission."
                ),
                error_code=(
                    "INVALID_PURCHASE_REQUEST_STATE"
                ),
                data=purchase_request,
            )

        purchase_request.status = "SUBMITTED"

        self.service.update(
            purchase_request
        )

        return ExecutionResult.success_result(
            data=purchase_request,
            message=(
                "Purchase Request submitted successfully."
            ),
            metadata={
                "purchase_request_id": (
                    purchase_request.id
                ),
                "previous_status": "DRAFT",
                "new_status": "SUBMITTED",
                "operation": context.operation,
            },
        )


class ApprovePurchaseRequestHandler(
    BaseCommandHandler,
):
    """
    Handle Purchase Request approval.
    """

    command_type = (
        ApprovePurchaseRequestCommand
    )

    def __init__(
        self,
        service: PurchaseRequestService | None = None,
    ) -> None:
        self.service = (
            service
            or PurchaseRequestService()
        )

    def handle(
        self,
        command: ApprovePurchaseRequestCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Approve a Purchase Request from
        SUBMITTED to APPROVED.
        """

        purchase_request = self.service.get(
            command.purchase_request_id
        )

        if purchase_request.status != "SUBMITTED":
            return ExecutionResult.failure_result(
                message=(
                    "Purchase Request must be in "
                    "SUBMITTED status before approval."
                ),
                error_code=(
                    "INVALID_PURCHASE_REQUEST_STATE"
                ),
                data=purchase_request,
            )

        purchase_request.status = "APPROVED"

        self.service.update(
            purchase_request
        )

        return ExecutionResult.success_result(
            data=purchase_request,
            message=(
                "Purchase Request approved successfully."
            ),
            metadata={
                "purchase_request_id": (
                    purchase_request.id
                ),
                "previous_status": "SUBMITTED",
                "new_status": "APPROVED",
                "operation": context.operation,
            },
        )


__all__ = [
    "ApprovePurchaseRequestHandler",
    "SubmitPurchaseRequestHandler",
]
