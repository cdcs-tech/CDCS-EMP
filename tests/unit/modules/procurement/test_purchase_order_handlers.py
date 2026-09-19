"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow command handler tests.
"""

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
    purchase_order = Mock()
    purchase_order.id = 7
    purchase_order.status = source_status

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

    handler = handler_class(service=service)
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

    assert result.metadata == {
        "purchase_order_id": 7,
        "previous_status": source_status,
        "new_status": target_status,
        "operation": operation,
    }

    service.get.assert_called_once_with(7)
    getattr(
        service,
        method_name,
    ).assert_called_once_with(purchase_order)


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
            "SUBMITTED",
            "Purchase Order must be in APPROVED status before cancellation.",
        ),
    ],
)
def test_purchase_order_handler_translates_invalid_state_to_failure_result(
    handler_class,
    command_class,
    method_name,
    operation,
    source_status,
    failure_message,
):
    service = Mock()
    purchase_order = Mock()
    purchase_order.id = 7
    purchase_order.status = source_status

    service.get.return_value = purchase_order

    getattr(
        service,
        method_name,
    ).side_effect = ValueError(
        "Invalid workflow transition."
    )

    handler = handler_class(service=service)
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
