"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration

Partial Purchase Order receipt handling tests.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from app.core.execution.context import ExecutionContext
from app.core.integration import (
    IntegrationResponse,
)
from app.modules.procurement.commands.purchase_order_receive import (
    ReceivePurchaseOrderCommand,
)
from app.modules.procurement.handlers.purchase_order_receive import (
    ReceivePurchaseOrderHandler,
)


@dataclass
class FakePurchaseOrder:
    id: int
    status: str


class FakePurchaseOrderService:
    def __init__(self, purchase_order):
        self.purchase_order = purchase_order

    def get(self, purchase_order_id):
        assert purchase_order_id == self.purchase_order.id
        return self.purchase_order


class FakeIntegrationResult:
    def __init__(
        self,
        *,
        success=True,
        message="Inventory receipt posted successfully.",
    ):
        self.success = success
        self.failed = not success
        self.message = message
        self.provider = "inventory"
        self.operation = "receive_purchase_order"
        self.response = IntegrationResponse(
            success=success,
            message=message,
            request_id="integration-test",
        )


class FakeIntegrationLifecycle:
    def __init__(self):
        self.requests = []
        self.subjects = []

    def execute(self, request, subject=""):
        self.requests.append(request)
        self.subjects.append(subject)
        return FakeIntegrationResult()


def build_command(
    *,
    quantity_received,
    receiving_reference,
    idempotency_key,
):
    return ReceivePurchaseOrderCommand(
        purchase_order_id=10,
        purchase_order_reference="PO-2026-001",
        purchase_order_line_reference="PO-2026-001-L1",
        stock_item_reference="STOCK-001",
        inventory_location_reference="MAIN",
        quantity_received=quantity_received,
        unit="kg",
        received_at=datetime(
            2026,
            9,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        receiving_reference=receiving_reference,
        idempotency_key=idempotency_key,
        notes=None,
    )


def build_handler(
    *,
    purchase_order=None,
):
    purchase_order = purchase_order or FakePurchaseOrder(
        id=10,
        status="APPROVED",
    )

    integration_lifecycle = FakeIntegrationLifecycle()

    handler = ReceivePurchaseOrderHandler(
        service=FakePurchaseOrderService(
            purchase_order,
        ),
        integration_lifecycle=integration_lifecycle,
    )

    return handler, integration_lifecycle, purchase_order


def build_context():
    return ExecutionContext(
        user_id="user-1",
        module_name="PROCUREMENT",
        operation="procurement.purchase_order.receive",
    )


def test_partial_receipt_smaller_than_ordered_quantity_is_accepted():
    """
    A receipt may represent less than the ordered Purchase Order
    Line quantity.
    """
    handler, integration_lifecycle, purchase_order = build_handler()

    command = build_command(
        quantity_received=Decimal("30.000"),
        receiving_reference="GRN-001",
        idempotency_key="receipt-001",
    )

    result = handler.handle(
        command,
        build_context(),
    )

    assert result.success is True
    assert purchase_order.status == "APPROVED"
    assert len(integration_lifecycle.requests) == 1

    receipt = (
        integration_lifecycle.requests[0].payload
    )

    assert receipt.quantity_received == Decimal(
        "30.000"
    )


def test_multiple_partial_receipts_are_independent_operations():
    """
    Multiple partial receipts for the same Purchase Order Line
    are communicated as independent receiving operations.
    """
    handler, integration_lifecycle, purchase_order = build_handler()

    first_command = build_command(
        quantity_received=Decimal("30.000"),
        receiving_reference="GRN-001",
        idempotency_key="receipt-001",
    )

    second_command = build_command(
        quantity_received=Decimal("40.000"),
        receiving_reference="GRN-002",
        idempotency_key="receipt-002",
    )

    first_result = handler.handle(
        first_command,
        build_context(),
    )

    second_result = handler.handle(
        second_command,
        build_context(),
    )

    assert first_result.success is True
    assert second_result.success is True

    assert purchase_order.status == "APPROVED"

    assert len(
        integration_lifecycle.requests
    ) == 2

    first_receipt = (
        integration_lifecycle.requests[0].payload
    )
    second_receipt = (
        integration_lifecycle.requests[1].payload
    )

    assert first_receipt.quantity_received == Decimal(
        "30.000"
    )
    assert second_receipt.quantity_received == Decimal(
        "40.000"
    )

    assert (
        first_receipt.receiving_reference
        == "GRN-001"
    )
    assert (
        second_receipt.receiving_reference
        == "GRN-002"
    )

    assert (
        first_receipt.idempotency_key
        != second_receipt.idempotency_key
    )


def test_partial_receipts_do_not_change_purchase_order_workflow_state():
    """
    Receiving a partial quantity does not transition the Purchase
    Order workflow.
    """
    handler, integration_lifecycle, purchase_order = build_handler()

    command = build_command(
        quantity_received=Decimal("25.000"),
        receiving_reference="GRN-003",
        idempotency_key="receipt-003",
    )

    result = handler.handle(
        command,
        build_context(),
    )

    assert result.success is True
    assert purchase_order.status == "APPROVED"
    assert len(integration_lifecycle.requests) == 1


def test_partial_receipts_do_not_require_quantity_equal_to_ordered_quantity():
    """
    The receiving contract communicates the current receipt quantity
    independently from the Purchase Order Line ordered quantity.
    """
    handler, integration_lifecycle, purchase_order = build_handler()

    command = build_command(
        quantity_received=Decimal("0.500"),
        receiving_reference="GRN-004",
        idempotency_key="receipt-004",
    )

    result = handler.handle(
        command,
        build_context(),
    )

    assert result.success is True
    assert purchase_order.status == "APPROVED"

    receipt = (
        integration_lifecycle.requests[0].payload
    )

    assert receipt.quantity_received == Decimal(
        "0.500"
    )


def test_partial_receipts_do_not_create_procurement_cumulative_state():
    """
    The receiving handler delegates individual receipt quantities
    without maintaining cumulative receipt state.
    """
    handler, integration_lifecycle, purchase_order = build_handler()

    first_command = build_command(
        quantity_received=Decimal("20.000"),
        receiving_reference="GRN-005",
        idempotency_key="receipt-005",
    )

    second_command = build_command(
        quantity_received=Decimal("15.000"),
        receiving_reference="GRN-006",
        idempotency_key="receipt-006",
    )

    first_result = handler.handle(
        first_command,
        build_context(),
    )

    second_result = handler.handle(
        second_command,
        build_context(),
    )

    assert first_result.success is True
    assert second_result.success is True

    assert purchase_order.status == "APPROVED"
    assert len(integration_lifecycle.requests) == 2

    assert not hasattr(
        purchase_order,
        "received_quantity",
    )

    assert not hasattr(
        purchase_order,
        "receipt_total",
    )
