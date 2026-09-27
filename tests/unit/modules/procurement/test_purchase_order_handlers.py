"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow command handler tests.
"""

from datetime import date, datetime
from unittest.mock import Mock

import pytest

from app.core.execution.context import ExecutionContext
from app.core.execution.results import ExecutionResult
from app.modules.procurement.commands import (
    ApprovePurchaseOrderCommand,
    CancelPurchaseOrderCommand,
    RejectPurchaseOrderCommand,
    ReturnPurchaseOrderCommand,
    SubmitPurchaseOrderCommand,
)
from app.modules.procurement.handlers import (
    ApprovePurchaseOrderHandler,
    CancelPurchaseOrderHandler,
    RejectPurchaseOrderHandler,
    ReturnPurchaseOrderHandler,
    SubmitPurchaseOrderHandler,
)
from app.modules.procurement.models import PurchaseOrder
from app.modules.procurement.services import (
    ProcurementFinanceCommitmentService,
)


def _context(
    operation: str,
) -> ExecutionContext:
    context = Mock(spec=ExecutionContext)
    context.operation = operation
    return context


@pytest.mark.parametrize(
    (
        "handler_class",
        "command_class",
        "method_name",
        "operation",
        "source_status",
        "target_status",
        "success_message",
    ),
    [
        (
            SubmitPurchaseOrderHandler,
            SubmitPurchaseOrderCommand,
            "submit",
            "purchase_order.submit",
            "DRAFT",
            "SUBMITTED",
            "Purchase Order submitted successfully.",
        ),
        (
            ApprovePurchaseOrderHandler,
            ApprovePurchaseOrderCommand,
            "approve",
            "purchase_order.approve",
            "SUBMITTED",
            "APPROVED",
            "Purchase Order approved successfully.",
        ),
        (
            RejectPurchaseOrderHandler,
            RejectPurchaseOrderCommand,
            "reject",
            "purchase_order.reject",
            "SUBMITTED",
            "REJECTED",
            "Purchase Order rejected successfully.",
        ),
        (
            ReturnPurchaseOrderHandler,
            ReturnPurchaseOrderCommand,
            "return_to_draft",
            "purchase_order.return",
            "SUBMITTED",
            "DRAFT",
            "Purchase Order returned to draft successfully.",
        ),
        (
            CancelPurchaseOrderHandler,
            CancelPurchaseOrderCommand,
            "cancel",
            "purchase_order.cancel",
            "APPROVED",
            "CANCELLED",
            "Purchase Order cancelled successfully.",
        ),
    ],
)
def test_purchase_order_handler_returns_success_result(
    handler_class,
    command_class,
    method_name,
    operation,
    source_status,
    target_status,
    success_message,
):
    service = Mock()

    if handler_class is ApprovePurchaseOrderHandler:
        purchase_order = PurchaseOrder(
            id=7,
            supplier_id=501,
            reference="PO-2026-007",
            order_date=date(2026, 9, 26),
            status=source_status,
            purchase_request_id=601,
        )
        commitment_service = Mock(
            spec=ProcurementFinanceCommitmentService
        )
        commitment_service.register.return_value = Mock()
        handler = handler_class(
            service=service,
            commitment_service=commitment_service,
        )
    else:
        purchase_order = Mock()
        purchase_order.id = 7
        purchase_order.status = source_status
        handler = handler_class(
            service=service
        )

    service.get.return_value = purchase_order

    def transition(
        entity,
    ):
        entity.status = target_status
        return entity

    getattr(
        service,
        method_name,
    ).side_effect = transition

    command = command_class(7)
    context = _context(operation)

    result = handler.handle(
        command,
        context,
    )

    assert isinstance(
        result,
        ExecutionResult,
    )
    assert result.success is True
    assert result.data is purchase_order
    assert result.message == success_message

    expected_metadata = {
        "purchase_order_id": 7,
        "previous_status": source_status,
        "new_status": target_status,
        "operation": operation,
    }

    if handler_class is ApprovePurchaseOrderHandler:
        assert "approved_at" in result.metadata
        assert isinstance(
            result.metadata["approved_at"],
            datetime,
        )
        assert result.metadata["approved_at"].tzinfo is not None
        assert (
            result.metadata["approved_at"].utcoffset()
            is not None
        )
        expected_metadata["approved_at"] = (
            result.metadata["approved_at"]
        )

        commitment_service.register.assert_called_once_with(
            purchase_order
        )

    assert result.metadata == expected_metadata

    service.get.assert_called_once_with(7)
    getattr(
        service,
        method_name,
    ).assert_called_once_with(purchase_order)

    assert purchase_order.status == target_status


@pytest.mark.parametrize(
    (
        "handler_class",
        "command_class",
        "method_name",
        "operation",
        "source_status",
        "failure_message",
    ),
    [
        (
            SubmitPurchaseOrderHandler,
            SubmitPurchaseOrderCommand,
            "submit",
            "purchase_order.submit",
            "SUBMITTED",
            "Purchase Order must be in DRAFT status before submission.",
        ),
        (
            ApprovePurchaseOrderHandler,
            ApprovePurchaseOrderCommand,
            "approve",
            "purchase_order.approve",
            "DRAFT",
            "Purchase Order must be in SUBMITTED status before approval.",
        ),
        (
            RejectPurchaseOrderHandler,
            RejectPurchaseOrderCommand,
            "reject",
            "purchase_order.reject",
            "APPROVED",
            "Purchase Order must be in SUBMITTED status before rejection.",
        ),
        (
            ReturnPurchaseOrderHandler,
            ReturnPurchaseOrderCommand,
            "return_to_draft",
            "purchase_order.return",
            "APPROVED",
            "Purchase Order must be in SUBMITTED status before return.",
        ),
        (
            CancelPurchaseOrderHandler,
            CancelPurchaseOrderCommand,
            "cancel",
            "purchase_order.cancel",
            "DRAFT",
            "Purchase Order must be in APPROVED status before cancellation.",
        ),
    ],
)
def test_purchase_order_handler_rejects_invalid_state(
    handler_class,
    command_class,
    method_name,
    operation,
    source_status,
    failure_message,
):
    service = Mock()

    if handler_class is ApprovePurchaseOrderHandler:
        purchase_order = PurchaseOrder(
            id=7,
            supplier_id=501,
            reference="PO-2026-007",
            order_date=date(2026, 9, 26),
            status=source_status,
            purchase_request_id=601,
        )
        commitment_service = Mock(
            spec=ProcurementFinanceCommitmentService
        )
        handler = handler_class(
            service=service,
            commitment_service=commitment_service,
        )
    else:
        purchase_order = Mock()
        purchase_order.id = 7
        purchase_order.status = source_status
        handler = handler_class(
            service=service
        )

    service.get.return_value = purchase_order

    getattr(
        service,
        method_name,
    ).side_effect = ValueError(
        failure_message,
    )

    command = command_class(7)
    context = _context(operation)

    result = handler.handle(
        command,
        context,
    )

    assert isinstance(
        result,
        ExecutionResult,
    )
    assert result.success is False
    assert result.data is purchase_order
    assert result.message == failure_message
    assert result.error_code == (
        "INVALID_PURCHASE_ORDER_STATE"
    )
    assert result.metadata == {}

    service.get.assert_called_once_with(7)
    getattr(
        service,
        method_name,
    ).assert_called_once_with(purchase_order)

    assert purchase_order.status == source_status

    if handler_class is ApprovePurchaseOrderHandler:
        commitment_service.register.assert_not_called()


def test_approve_purchase_order_registers_finance_commitment_after_approval():
    service = Mock()

    purchase_order = PurchaseOrder(
        id=7,
        supplier_id=501,
        reference="PO-2026-007",
        order_date=date(2026, 9, 26),
        status="SUBMITTED",
        purchase_request_id=601,
    )

    commitment_service = Mock(
        spec=ProcurementFinanceCommitmentService
    )
    commitment_service.register.return_value = Mock()

    def approve(entity):
        entity.status = "APPROVED"
        return entity

    service.get.return_value = purchase_order
    service.approve.side_effect = approve

    handler = ApprovePurchaseOrderHandler(
        service=service,
        commitment_service=commitment_service,
    )

    result = handler.handle(
        ApprovePurchaseOrderCommand(7),
        _context("purchase_order.approve"),
    )

    assert result.success is True
    assert result.data is purchase_order
    assert purchase_order.status == "APPROVED"

    service.approve.assert_called_once_with(
        purchase_order
    )
    commitment_service.register.assert_called_once_with(
        purchase_order
    )


def test_approve_purchase_order_commitment_failure_propagates():
    service = Mock()

    purchase_order = PurchaseOrder(
        id=7,
        supplier_id=501,
        reference="PO-2026-007",
        order_date=date(2026, 9, 26),
        status="SUBMITTED",
        purchase_request_id=601,
    )

    commitment_service = Mock(
        spec=ProcurementFinanceCommitmentService
    )
    commitment_service.register.side_effect = RuntimeError(
        "Finance commitment registration failed."
    )

    def approve(entity):
        entity.status = "APPROVED"
        return entity

    service.get.return_value = purchase_order
    service.approve.side_effect = approve

    handler = ApprovePurchaseOrderHandler(
        service=service,
        commitment_service=commitment_service,
    )

    with pytest.raises(
        RuntimeError,
        match="Finance commitment registration failed.",
    ):
        handler.handle(
            ApprovePurchaseOrderCommand(7),
            _context("purchase_order.approve"),
        )

    assert purchase_order.status == "APPROVED"
    service.approve.assert_called_once_with(
        purchase_order
    )
    commitment_service.register.assert_called_once_with(
        purchase_order
    )
