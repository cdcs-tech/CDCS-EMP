"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Procurement → Finance post-commit integration tests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.core.execution.context import ExecutionContext
from app.core.execution.results import ExecutionResult

from app.modules.procurement.commands.purchase_order import (
    ApprovePurchaseOrderCommand,
)
from app.modules.procurement.integration.post_commit import (
    ProcurementFinancePostCommitExecutor,
)
from app.modules.procurement.models.purchase_order import (
    PurchaseOrder,
)
from app.modules.procurement.services.finance_commitment import (
    ProcurementFinanceCommitmentService,
)


def build_purchase_order() -> PurchaseOrder:
    purchase_order = MagicMock(spec=PurchaseOrder)

    purchase_order.id = 701
    purchase_order.reference = "PO-2026-0001"
    purchase_order.status = "APPROVED"

    return purchase_order


def build_context() -> ExecutionContext:
    return ExecutionContext(
        user_id="test-user",
        operation="procurement.purchase_order.approve",
    )


def build_success_result(
    purchase_order: PurchaseOrder,
) -> ExecutionResult:
    approved_at = datetime(
        2026,
        9,
        20,
        14,
        30,
        tzinfo=timezone.utc,
    )

    return ExecutionResult.success_result(
        data=purchase_order,
        metadata={
            "purchase_order_id": purchase_order.id,
            "previous_status": "SUBMITTED",
            "new_status": "APPROVED",
            "operation": "APPROVE_PURCHASE_ORDER",
            "approved_at": approved_at,
        },
    )


def build_commitment_service():
    service = MagicMock(
        spec=ProcurementFinanceCommitmentService,
    )

    commitment = MagicMock()
    service.get_by_purchase_order_id.return_value = commitment

    return service, commitment


def test_executor_submits_registered_finance_commitment_for_approved_purchase_order():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    commitment_service, commitment = (
        build_commitment_service()
    )

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        context,
        result,
    )

    commitment_service.get_by_purchase_order_id.assert_called_once_with(
        purchase_order.id
    )

    commitment_service.deliver.assert_called_once_with(
        commitment,
        purchase_order,
        subject=context.user_id,
        approved_at=datetime(
            2026,
            9,
            20,
            14,
            30,
            tzinfo=timezone.utc,
        ),
    )


def test_executor_sets_procurement_context_on_commitment_delivery():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    commitment_service, commitment = (
        build_commitment_service()
    )

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        context,
        result,
    )

    delivery_call = (
        commitment_service.deliver.call_args
    )

    assert delivery_call.kwargs["subject"] == (
        context.user_id
    )


def test_executor_ignores_non_approval_commands():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    commitment_service, _commitment = (
        build_commitment_service()
    )

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    executor.execute(
        object(),
        context,
        result,
    )

    commitment_service.get_by_purchase_order_id.assert_not_called()
    commitment_service.deliver.assert_not_called()


def test_executor_ignores_unsuccessful_approval_result():
    purchase_order = build_purchase_order()

    result = ExecutionResult.failure_result(
        message="Purchase Order approval failed.",
    )

    commitment_service, _commitment = (
        build_commitment_service()
    )

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        build_context(),
        result,
    )

    commitment_service.get_by_purchase_order_id.assert_not_called()
    commitment_service.deliver.assert_not_called()


def test_executor_requires_approval_timestamp():
    purchase_order = build_purchase_order()

    result = ExecutionResult.success_result(
        data=purchase_order,
        metadata={
            "purchase_order_id": purchase_order.id,
            "new_status": "APPROVED",
        },
    )

    commitment_service, _commitment = (
        build_commitment_service()
    )

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    with pytest.raises(
        ValueError,
        match="approved_at",
    ):
        executor.execute(
            ApprovePurchaseOrderCommand(
                purchase_order_id=purchase_order.id,
            ),
            build_context(),
            result,
        )

    commitment_service.get_by_purchase_order_id.assert_not_called()
    commitment_service.deliver.assert_not_called()


def test_executor_requires_registered_finance_commitment():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    commitment_service = MagicMock(
        spec=ProcurementFinanceCommitmentService,
    )
    commitment_service.get_by_purchase_order_id.return_value = None

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    with pytest.raises(
        ValueError,
        match="registered Finance commitment",
    ):
        executor.execute(
            ApprovePurchaseOrderCommand(
                purchase_order_id=purchase_order.id,
            ),
            context,
            result,
        )

    commitment_service.get_by_purchase_order_id.assert_called_once_with(
        purchase_order.id
    )
    commitment_service.deliver.assert_not_called()


def test_executor_propagates_commitment_delivery_failure():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    commitment_service, commitment = (
        build_commitment_service()
    )

    commitment_service.deliver.side_effect = RuntimeError(
        "Finance provider unavailable."
    )

    executor = ProcurementFinancePostCommitExecutor(
        commitment_service=commitment_service,
    )

    with pytest.raises(
        RuntimeError,
        match="Finance provider unavailable",
    ):
        executor.execute(
            ApprovePurchaseOrderCommand(
                purchase_order_id=purchase_order.id,
            ),
            context,
            result,
        )

    commitment_service.get_by_purchase_order_id.assert_called_once_with(
        purchase_order.id
    )

    commitment_service.deliver.assert_called_once_with(
        commitment,
        purchase_order,
        subject=context.user_id,
        approved_at=datetime(
            2026,
            9,
            20,
            14,
            30,
            tzinfo=timezone.utc,
        ),
    )
