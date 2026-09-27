"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Procurement → Finance post-commit integration.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.execution.context import ExecutionContext
from app.core.execution.post_commit import PostCommitExecutor
from app.core.execution.results import ExecutionResult

from app.modules.procurement.commands.purchase_order import (
    ApprovePurchaseOrderCommand,
)
from app.modules.procurement.models.purchase_order import (
    PurchaseOrder,
)
from app.modules.procurement.repositories import (
    ProcurementFinanceCommitmentRepository,
)
from app.modules.procurement.services import (
    ProcurementFinanceCommitmentService,
)


class ProcurementFinancePostCommitExecutor(
    PostCommitExecutor,
):
    """
    Executes the Procurement → Finance integration after
    successful Purchase Order approval commit.

    The originating Procurement transaction is already committed
    before this executor is invoked.

    Commitment lifecycle ownership remains with
    ProcurementFinanceCommitmentService. The executor therefore
    delegates Finance delivery to that service rather than
    maintaining a second delivery or state-transition path.

    Post-commit failures are isolated by CommandDispatcher and
    cannot roll back the already-committed Procurement transaction.
    """

    def __init__(
        self,
        commitment_service: (
            ProcurementFinanceCommitmentService | None
        ) = None,
    ) -> None:
        self.commitment_service = (
            commitment_service
            or ProcurementFinanceCommitmentService()
        )

        if not isinstance(
            self.commitment_service,
            ProcurementFinanceCommitmentService,
        ):
            raise TypeError(
                "commitment_service must be a "
                "ProcurementFinanceCommitmentService."
            )

    def execute(
        self,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Deliver the registered Finance commitment after
        successful Purchase Order approval commit.

        Non-approval commands are ignored.

        The Purchase Order approval timestamp is taken from
        the successful command result metadata.

        Finance delivery and commitment lifecycle state
        transitions are delegated to
        ProcurementFinanceCommitmentService.
        """

        if not isinstance(
            command,
            ApprovePurchaseOrderCommand,
        ):
            return

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise TypeError(
                "context must be an ExecutionContext."
            )

        if not isinstance(
            result,
            ExecutionResult,
        ):
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

        approved_at = self._approved_at(
            result
        )

        commitment = (
            self.commitment_service.get_by_purchase_order_id(
                purchase_order.id
            )
        )

        if commitment is None:
            raise ValueError(
                "Approved Purchase Order does not have a "
                "registered Finance commitment."
            )

        self.commitment_service.deliver(
            commitment,
            purchase_order,
            subject=context.user_id,
            approved_at=approved_at,
        )

    @staticmethod
    def _approved_at(
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

        if not isinstance(
            approved_at,
            datetime,
        ):
            raise ValueError(
                "Purchase Order approval result does not "
                "contain a valid approved_at timestamp."
            )

        return approved_at


__all__ = [
    "ProcurementFinancePostCommitExecutor",
]
