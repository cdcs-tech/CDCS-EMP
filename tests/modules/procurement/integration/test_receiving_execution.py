"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Tests for the Purchase Order Receiving Execution Boundary.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.core.execution.context import ExecutionContext
from app.core.execution.commands.types import CommandType
from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
)
from app.modules.procurement.commands.purchase_order_receive import (
    ReceivePurchaseOrderCommand,
)
from app.modules.procurement.handlers.purchase_order_receive import (
    ReceivePurchaseOrderHandler,
)
from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)


# ---------------------------------------------------------------------------
# Test Doubles
# ---------------------------------------------------------------------------


class FakePurchaseOrder:
    """Minimal Purchase Order representation for handler tests."""

    def __init__(
        self,
        *,
        purchase_order_id: int = 101,
        status: str = "APPROVED",
    ) -> None:
        self.id = purchase_order_id
        self.status = status


class FakePurchaseOrderService:
    """Minimal Purchase Order service test double."""

    def __init__(
        self,
        purchase_order: FakePurchaseOrder | None = None,
    ) -> None:
        self.purchase_order = (
            purchase_order
            or FakePurchaseOrder()
        )
        self.requested_ids: list[int] = []

    def get(
        self,
        purchase_order_id: int,
    ) -> FakePurchaseOrder:
        self.requested_ids.append(
            purchase_order_id
        )
        return self.purchase_order


class FakeIntegrationLifecycle:
    """
    Minimal IntegrationLifecycle test double.

    Records the IntegrationRequest received by the
    Procurement receiving handler and returns a
    controlled IntegrationResult.
    """

    def __init__(
        self,
        result: IntegrationResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.requests: list[IntegrationRequest] = []
        self.subjects: list[str] = []

    def execute(
        self,
        request: IntegrationRequest,
        subject: str = "",
    ) -> IntegrationResult:
        self.requests.append(request)
        self.subjects.append(subject)

        if self.error is not None:
            raise self.error

        if self.result is None:
            raise AssertionError(
                "FakeIntegrationLifecycle requires "
                "a result unless an error is configured."
            )

        return self.result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def received_at() -> datetime:
    """Provide a timezone-aware receiving timestamp."""

    return datetime(
        2026,
        9,
        20,
        10,
        30,
        tzinfo=timezone.utc,
    )


@pytest.fixture
def command(
    received_at: datetime,
) -> ReceivePurchaseOrderCommand:
    """Build a valid Purchase Order receiving command."""

    return ReceivePurchaseOrderCommand(
        purchase_order_id=101,
        purchase_order_reference="PO-2026-001",
        purchase_order_line_reference="POL-2026-001-01",
        stock_item_reference="ITEM-001",
        inventory_location_reference="STORE-JUBA",
        quantity_received=Decimal("25.000"),
        unit="kg",
        received_at=received_at,
        receiving_reference="GRN-2026-001",
        idempotency_key="GRN-2026-001:POL-2026-001-01",
        notes="Initial partial receipt.",
    )


@pytest.fixture
def context() -> ExecutionContext:
    """Build a valid execution context for receiving tests."""

    return ExecutionContext(
        user_id="test-user",
        module_name="PROCUREMENT",
        operation="procurement.purchase_order.receive",
    )


@pytest.fixture
def successful_result(
    command: ReceivePurchaseOrderCommand,
) -> IntegrationResult:
    """Build a successful integration result."""

    request = IntegrationRequest(
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=(
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        ),
        payload=None,
    )

    response = IntegrationResponse(
        success=True,
        status_code=200,
        data={
            "receiving_reference": (
                command.receiving_reference
            ),
        },
        message="Receipt accepted by Inventory.",
    )

    return IntegrationResult(
        request=request,
        response=response,
        duration_ms=1.25,
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=(
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        ),
    )


@pytest.fixture
def rejected_result() -> IntegrationResult:
    """Build a rejected integration result."""

    request = IntegrationRequest(
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=(
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        ),
        payload=None,
    )

    response = IntegrationResponse(
        success=False,
        status_code=400,
        message="Inventory rejected the receipt.",
        error="INVALID_INVENTORY_RECEIPT",
    )

    return IntegrationResult(
        request=request,
        response=response,
        duration_ms=1.10,
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=(
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        ),
    )


@pytest.fixture
def approved_purchase_order_service():
    """Provide a service containing an approved Purchase Order."""

    return FakePurchaseOrderService(
        FakePurchaseOrder(
            purchase_order_id=101,
            status="APPROVED",
        )
    )


@pytest.fixture
def receiving_handler(
    approved_purchase_order_service,
    successful_result,
):
    """Build a receiving handler with controlled dependencies."""

    integration_lifecycle = FakeIntegrationLifecycle(
        result=successful_result
    )

    handler = ReceivePurchaseOrderHandler(
        service=approved_purchase_order_service,
        integration_lifecycle=integration_lifecycle,
    )

    return (
        handler,
        approved_purchase_order_service,
        integration_lifecycle,
    )


# ---------------------------------------------------------------------------
# Command Tests
# ---------------------------------------------------------------------------


def test_receive_purchase_order_command_has_expected_name():
    """The receiving operation must use the dedicated execution name."""

    assert (
        ReceivePurchaseOrderCommand.command_name
        == "procurement.purchase_order.receive"
    )


def test_receive_purchase_order_command_uses_execute_type():
    """Receiving must be an execution command, not a workflow command."""

    assert (
        ReceivePurchaseOrderCommand.command_type
        == CommandType.EXECUTE
    )


def test_receive_purchase_order_command_uses_integration_metadata():
    """Receiving must be classified as an integration operation."""

    metadata = (
        ReceivePurchaseOrderCommand.metadata
    )

    assert metadata is not None
    assert metadata.category == "integration"


def test_receive_purchase_order_command_validates_positive_id(
    command: ReceivePurchaseOrderCommand,
):
    """A Purchase Order ID must be a positive integer."""

    command.validate()

    assert command.purchase_order_id == 101


@pytest.mark.parametrize(
    "purchase_order_id",
    [0, -1],
)
def test_receive_purchase_order_command_rejects_non_positive_id(
    command: ReceivePurchaseOrderCommand,
    purchase_order_id: int,
):
    """Non-positive Purchase Order IDs must be rejected."""

    command.purchase_order_id = purchase_order_id

    with pytest.raises(ValueError):
        command.validate()


def test_receive_purchase_order_command_rejects_non_integer_id(
    command: ReceivePurchaseOrderCommand,
):
    """Purchase Order ID must be an integer."""

    command.purchase_order_id = "101"  # type: ignore[assignment]

    with pytest.raises(ValueError):
        command.validate()


# ---------------------------------------------------------------------------
# Handler — Purchase Order State
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status",
    [
        "DRAFT",
        "SUBMITTED",
        "REJECTED",
        "CANCELLED",
    ],
)
def test_handler_rejects_receipt_for_non_approved_purchase_order(
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
    status: str,
):
    """Receiving must only be allowed for an approved Purchase Order."""

    purchase_order = FakePurchaseOrder(
        purchase_order_id=101,
        status=status,
    )

    purchase_order_service = FakePurchaseOrderService(
        purchase_order
    )

    integration_lifecycle = FakeIntegrationLifecycle(
        result=None
    )

    handler = ReceivePurchaseOrderHandler(
        service=purchase_order_service,
        integration_lifecycle=integration_lifecycle,
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is False
    assert (
        result.error_code
        == "INVALID_PURCHASE_ORDER_STATE"
    )
    assert integration_lifecycle.requests == []


# ---------------------------------------------------------------------------
# Handler — Contract Construction
# ---------------------------------------------------------------------------


def test_handler_builds_purchase_order_receipt_request(
    receiving_handler,
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """The handler must construct the approved domain receipt contract."""

    handler, _, integration_lifecycle = (
        receiving_handler
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is True
    assert len(integration_lifecycle.requests) == 1

    request = integration_lifecycle.requests[0]

    assert isinstance(
        request.payload,
        PurchaseOrderReceiptRequest,
    )

    receipt = request.payload

    assert (
        receipt.purchase_order_reference
        == "PO-2026-001"
    )
    assert (
        receipt.purchase_order_line_reference
        == "POL-2026-001-01"
    )
    assert (
        receipt.stock_item_reference
        == "ITEM-001"
    )
    assert (
        receipt.inventory_location_reference
        == "STORE-JUBA"
    )
    assert (
        receipt.quantity_received
        == Decimal("25.000")
    )
    assert receipt.unit == "kg"
    assert (
        receipt.receiving_reference
        == "GRN-2026-001"
    )
    assert (
        receipt.idempotency_key
        == "GRN-2026-001:POL-2026-001-01"
    )
    assert (
        receipt.notes
        == "Initial partial receipt."
    )


# ---------------------------------------------------------------------------
# Handler — Integration Envelope
# ---------------------------------------------------------------------------


def test_handler_creates_inventory_integration_request(
    receiving_handler,
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """The handler must use the approved IntegrationRequest envelope."""

    handler, _, integration_lifecycle = (
        receiving_handler
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is True
    assert len(integration_lifecycle.requests) == 1

    request = integration_lifecycle.requests[0]

    assert isinstance(
        request,
        IntegrationRequest,
    )
    assert (
        request.provider
        == INVENTORY_INTEGRATION_PROVIDER
    )
    assert (
        request.operation
        == INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
    )


def test_handler_places_execution_context_in_integration_metadata(
    receiving_handler,
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """The integration request must retain execution context."""

    handler, _, integration_lifecycle = (
        receiving_handler
    )

    handler.handle(
        command,
        context,
    )

    request = integration_lifecycle.requests[0]

    assert (
        request.metadata["module"]
        == "PROCUREMENT"
    )
    assert (
        request.metadata["purchase_order_id"]
        == 101
    )
    assert (
        request.metadata["operation"]
        == "procurement.purchase_order.receive"
    )


# ---------------------------------------------------------------------------
# Handler — Delegation
# ---------------------------------------------------------------------------


def test_handler_delegates_to_integration_lifecycle(
    receiving_handler,
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """The handler must delegate delivery through IntegrationLifecycle."""

    handler, purchase_order_service, integration_lifecycle = (
        receiving_handler
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is True
    assert purchase_order_service.requested_ids == [101]
    assert len(integration_lifecycle.requests) == 1
    assert integration_lifecycle.subjects == [context.user_id]


# ---------------------------------------------------------------------------
# Handler — Successful Integration
# ---------------------------------------------------------------------------


def test_handler_returns_success_for_successful_integration(
    receiving_handler,
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """A successful Inventory integration must produce a successful result."""

    handler, _, _ = receiving_handler

    result = handler.handle(
        command,
        context,
    )

    assert result.success is True
    assert (
        result.message
        == "Purchase Order receipt submitted "
        "to Inventory successfully."
    )


# ---------------------------------------------------------------------------
# Handler — Inventory Rejection
# ---------------------------------------------------------------------------


def test_handler_returns_rejection_when_inventory_rejects_receipt(
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
    rejected_result: IntegrationResult,
):
    """Inventory rejection must become a failed execution result."""

    purchase_order_service = FakePurchaseOrderService(
        FakePurchaseOrder(
            purchase_order_id=101,
            status="APPROVED",
        )
    )

    integration_lifecycle = FakeIntegrationLifecycle(
        result=rejected_result
    )

    handler = ReceivePurchaseOrderHandler(
        service=purchase_order_service,
        integration_lifecycle=integration_lifecycle,
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is False
    assert (
        result.error_code
        == "PURCHASE_ORDER_RECEIPT_REJECTED"
    )
    assert (
        result.message
        == "Inventory rejected the receipt."
    )


# ---------------------------------------------------------------------------
# Handler — Contract Validation
# ---------------------------------------------------------------------------


def test_handler_returns_failure_for_invalid_receipt_contract(
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """Invalid receipt data must be rejected before integration delivery."""

    command.quantity_received = Decimal("0")

    purchase_order_service = FakePurchaseOrderService(
        FakePurchaseOrder(
            purchase_order_id=101,
            status="APPROVED",
        )
    )

    integration_lifecycle = FakeIntegrationLifecycle(
        result=None
    )

    handler = ReceivePurchaseOrderHandler(
        service=purchase_order_service,
        integration_lifecycle=integration_lifecycle,
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is False
    assert (
        result.error_code
        == "INVALID_PURCHASE_ORDER_RECEIPT"
    )
    assert integration_lifecycle.requests == []


# ---------------------------------------------------------------------------
# Handler — Integration Failure
# ---------------------------------------------------------------------------


def test_handler_returns_failure_when_integration_lifecycle_raises(
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """Integration delivery exceptions must become failed execution results."""

    purchase_order_service = FakePurchaseOrderService(
        FakePurchaseOrder(
            purchase_order_id=101,
            status="APPROVED",
        )
    )

    integration_lifecycle = FakeIntegrationLifecycle(
        error=RuntimeError(
            "Inventory provider unavailable."
        )
    )

    handler = ReceivePurchaseOrderHandler(
        service=purchase_order_service,
        integration_lifecycle=integration_lifecycle,
    )

    result = handler.handle(
        command,
        context,
    )

    assert result.success is False
    assert (
        result.error_code
        == "PURCHASE_ORDER_RECEIPT_INTEGRATION_FAILED"
    )
    assert (
        "Inventory provider unavailable."
        in result.metadata["error"]
    )


# ---------------------------------------------------------------------------
# Architectural Invariants
# ---------------------------------------------------------------------------


def test_receiving_does_not_change_purchase_order_status(
    receiving_handler,
    command: ReceivePurchaseOrderCommand,
    context: ExecutionContext,
):
    """
    Receiving is not a Purchase Order workflow transition.

    The Purchase Order must remain APPROVED after the
    receiving execution boundary delegates the receipt.
    """

    handler, purchase_order_service, _ = (
        receiving_handler
    )

    purchase_order = (
        purchase_order_service.purchase_order
    )

    assert purchase_order.status == "APPROVED"

    result = handler.handle(
        command,
        context,
    )

    assert result.success is True
    assert purchase_order.status == "APPROVED"


def test_receiving_handler_does_not_depend_on_inventory_repositories(
    receiving_handler,
):
    """
    The receiving boundary must communicate through the
    IntegrationLifecycle rather than directly manipulating
    Inventory repositories.
    """

    handler, _, _ = receiving_handler

    assert hasattr(
        handler,
        "integration_lifecycle",
    )
    assert not hasattr(
        handler,
        "stock_balance_repository",
    )
    assert not hasattr(
        handler,
        "stock_movement_repository",
    )
