"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow command tests.
"""

import pytest

from app.core.execution.commands.types import CommandType
from app.modules.procurement.commands import (
    ApprovePurchaseOrderCommand,
    CancelPurchaseOrderCommand,
    RejectPurchaseOrderCommand,
    ReturnPurchaseOrderCommand,
    SubmitPurchaseOrderCommand,
)


@pytest.mark.parametrize(
    (
        "command_class",
        "command_name",
        "operation",
        "metadata_name",
    ),
    [
        (
            SubmitPurchaseOrderCommand,
            "procurement.purchase_order.submit",
            "purchase_order.submit",
            "Submit Purchase Order",
        ),
        (
            ApprovePurchaseOrderCommand,
            "procurement.purchase_order.approve",
            "purchase_order.approve",
            "Approve Purchase Order",
        ),
        (
            RejectPurchaseOrderCommand,
            "procurement.purchase_order.reject",
            "purchase_order.reject",
            "Reject Purchase Order",
        ),
        (
            ReturnPurchaseOrderCommand,
            "procurement.purchase_order.return",
            "purchase_order.return",
            "Return Purchase Order",
        ),
        (
            CancelPurchaseOrderCommand,
            "procurement.purchase_order.cancel",
            "purchase_order.cancel",
            "Cancel Purchase Order",
        ),
    ],
)
def test_purchase_order_workflow_command_contract(
    command_class,
    command_name,
    operation,
    metadata_name,
):
    command = command_class(1)

    assert command.command_name == command_name
    assert command.command_type is CommandType.EXECUTE
    assert command.metadata.name == metadata_name
    assert command.metadata.module_name == "PROCUREMENT"
    assert command.metadata.operation == operation
    assert command.metadata.version == "1.0"
    assert command.metadata.category == "workflow"
    assert command.execute_name() == command_name


@pytest.mark.parametrize(
    "command_class",
    [
        SubmitPurchaseOrderCommand,
        ApprovePurchaseOrderCommand,
        RejectPurchaseOrderCommand,
        ReturnPurchaseOrderCommand,
        CancelPurchaseOrderCommand,
    ],
)
def test_purchase_order_workflow_command_accepts_positive_id(
    command_class,
):
    command = command_class(1)

    command.validate()

    assert command.purchase_order_id == 1


@pytest.mark.parametrize(
    "command_class",
    [
        SubmitPurchaseOrderCommand,
        ApprovePurchaseOrderCommand,
        RejectPurchaseOrderCommand,
        ReturnPurchaseOrderCommand,
        CancelPurchaseOrderCommand,
    ],
)
@pytest.mark.parametrize(
    "purchase_order_id",
    [
        0,
        -1,
    ],
)
def test_purchase_order_workflow_command_rejects_non_positive_id(
    command_class,
    purchase_order_id,
):
    command = command_class(
        purchase_order_id
    )

    with pytest.raises(
        ValueError,
        match="purchase_order_id must be greater than zero",
    ):
        command.validate()


@pytest.mark.parametrize(
    "command_class",
    [
        SubmitPurchaseOrderCommand,
        ApprovePurchaseOrderCommand,
        RejectPurchaseOrderCommand,
        ReturnPurchaseOrderCommand,
        CancelPurchaseOrderCommand,
    ],
)
@pytest.mark.parametrize(
    "purchase_order_id",
    [
        "1",
        None,
        1.0,
    ],
)
def test_purchase_order_workflow_command_rejects_non_integer_id(
    command_class,
    purchase_order_id,
):
    command = command_class(
        purchase_order_id
    )

    with pytest.raises(
        ValueError,
        match="purchase_order_id must be an integer",
    ):
        command.validate()
