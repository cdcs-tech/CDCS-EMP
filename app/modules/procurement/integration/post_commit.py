"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement → Finance post-commit integration.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.execution.context import ExecutionContext
from app.core.execution.post_commit import PostCommitExecutor
from app.core.execution.results import ExecutionResult
from app.core.integration.lifecycle import IntegrationLifecycle
from app.core.integration.models import IntegrationRequest, IntegrationResult

from app.modules.procurement.commands.purchase_order import (
    ApprovePurchaseOrderCommand,
)
from app.modules.procurement.integration.contracts import (
    FINANCE_INTEGRATION_PROVIDER,
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
    ProcurementFinancialEffectLine,
    ProcurementFinancialEffectRequest,
)
from app.modules.procurement.models.purchase_order import PurchaseOrder


class ProcurementFinancePostCommitExecutor(PostCommitExecutor):
    """
    Executes the Procurement → Finance integration after
    successful Purchase Order approval commit.

    This executor does not own the originating transaction.
    Finance failures therefore cannot roll back or alter the
    already-committed Procurement transaction.

    IntegrationLifecycle owns the integration request/result
    observability boundary, including integration events and
    audit records.
    """

    def __init__(
        self,
        integration_lifecycle: IntegrationLifecycle,
        currency: str = "USD",
    ) -> None:
        if not isinstance(
            integration_lifecycle,
            IntegrationLifecycle,
        ):
            raise TypeError(
                "integration_lifecycle must be an "
                "IntegrationLifecycle."
            )

        if not isinstance(currency, str) or not currency.strip():
            raise ValueError(
                "currency must be a non-empty string."
            )

        self.integration_lifecycle = integration_lifecycle
        self.currency = currency.strip().upper()

    def execute(
        self,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Execute Finance communication for an approved
        Purchase Order.

        Non-approval commands are ignored.

        Integration failures are allowed to propagate to
        CommandDispatcher, whose post-commit boundary
        intentionally isolates them from the committed
        Procurement transaction.

        Provider-declared failures are returned by the
        IntegrationLifecycle as a failed IntegrationResult.
        They do not raise an exception by themselves.
        """

        if not isinstance(
            command,
            ApprovePurchaseOrderCommand,
        ):
            return

        if not isinstance(context, ExecutionContext):
            raise TypeError(
                "context must be an ExecutionContext."
            )

        if not isinstance(result, ExecutionResult):
            raise TypeError(
                "result must be an ExecutionResult."
            )

        if not result.is_success():
            return

        purchase_order = result.data

        if not isinstance(
            purchase_order,
            PurchaseOrder,
        ):
            raise TypeError(
                "Successful Purchase Order approval result "
                "must contain a PurchaseOrder."
            )

        approved_at = self._approved_at(result)

        payload = self._build_payload(
            purchase_order,
            approved_at,
        )

        request = IntegrationRequest(
            provider=FINANCE_INTEGRATION_PROVIDER,
            operation=FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
            payload=payload,
            metadata={
                "module": "PROCUREMENT",
                "purchase_order_id": purchase_order.id,
                "purchase_order_reference": (
                    purchase_order.reference
                ),
                "operation": context.operation,
                "subject": context.user_id,
            },
        )

        integration_result = self.integration_lifecycle.execute(
            request,
            subject=context.user_id,
        )

        if not isinstance(
            integration_result,
            IntegrationResult,
        ):
            raise TypeError(
                "IntegrationLifecycle must return an "
                "IntegrationResult."
            )

    def _approved_at(
        self,
        result: ExecutionResult,
    ) -> datetime:
        """
        Retrieve the approval timestamp captured by the
        Purchase Order approval handler.
        """

        metadata = result.metadata or {}

        approved_at = metadata.get(
            "approved_at"
        )

        if isinstance(
            approved_at,
            datetime,
        ):
            if approved_at.tzinfo is None:
                return approved_at.replace(
                    tzinfo=timezone.utc
                )

            return approved_at

        raise ValueError(
            "Purchase Order approval result does not "
            "contain a valid approved_at timestamp."
        )

    def _build_payload(
        self,
        purchase_order: PurchaseOrder,
        approved_at: datetime,
    ) -> ProcurementFinancialEffectRequest:
        """
        Convert the approved Procurement business fact into
        the Finance integration contract.
        """

        purchase_request = (
            purchase_order.purchase_request
        )

        supplier = purchase_order.supplier

        lines = tuple(
            self._build_line(line)
            for line in purchase_order.lines
        )

        total_value = sum(
            (
                Decimal(str(line.total_amount))
                for line in purchase_order.lines
            ),
            Decimal("0"),
        )

        return ProcurementFinancialEffectRequest(
            purchase_order_reference=(
                purchase_order.reference
            ),
            purchase_request_reference=(
                purchase_request.reference
            ),
            supplier_reference=supplier.code,
            purchase_order_date=datetime.combine(
                purchase_order.order_date,
                datetime.min.time(),
                tzinfo=timezone.utc,
            ),
            approved_at=approved_at,
            currency=self.currency,
            total_procurement_value=total_value,
            purchase_order_lines=lines,
            idempotency_key=(
                "procurement-commitment:"
                f"{purchase_order.reference}"
            ),
        )

    @staticmethod
    def _build_line(
        line: Any,
    ) -> ProcurementFinancialEffectLine:
        return ProcurementFinancialEffectLine(
            purchase_order_line_reference=(
                str(line.id)
            ),
            description=line.description,
            quantity=Decimal(str(line.quantity)),
            unit=line.unit,
            unit_price=Decimal(
                str(line.unit_price)
            ),
            line_amount=Decimal(
                str(line.total_amount)
            ),
        )


__all__ = [
    "ProcurementFinancePostCommitExecutor",
]
