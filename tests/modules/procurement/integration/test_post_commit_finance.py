"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement → Finance post-commit integration tests.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.core.execution.context import ExecutionContext
from app.core.execution.results import ExecutionResult
from app.core.integration.models import IntegrationRequest
from app.core.integration.service import IntegrationService
from app.modules.procurement.commands.purchase_order import (
    ApprovePurchaseOrderCommand,
)
from app.modules.procurement.integration.contracts import (
    FINANCE_INTEGRATION_PROVIDER,
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
)
from app.modules.procurement.integration.post_commit import (
    ProcurementFinancePostCommitExecutor,
)
from app.modules.procurement.models.purchase_order import (
    PurchaseOrder,
)
from app.modules.procurement.models.purchase_order_line import (
    PurchaseOrderLine,
)
from app.modules.procurement.models.purchase_request import (
    PurchaseRequest,
)
from app.modules.procurement.models.supplier import (
    Supplier,
)


class RecordingIntegrationService(IntegrationService):
    """
    IntegrationService test double that records requests
    without requiring a registered Finance provider.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[IntegrationRequest] = []

    def execute(
        self,
        request: IntegrationRequest,
    ):
        self.requests.append(request)

        return None


def build_purchase_order() -> PurchaseOrder:
    supplier = Supplier(
        name="Test Supplier",
        code="SUP-001",
        supplier_type="VENDOR",
        status="ACTIVE",
    )
    supplier.id = 501

    purchase_request = PurchaseRequest(
        reference="PR-2026-0001",
        purchase_requirement_id=1,
        request_date=date(2026, 9, 10),
        status="APPROVED",
    )
    purchase_request.id = 601

    purchase_order = PurchaseOrder(
        supplier_id=supplier.id,
        reference="PO-2026-0001",
        order_date=date(2026, 9, 15),
        purchase_request_id=purchase_request.id,
        status="APPROVED",
    )
    purchase_order.id = 701

    line_one = PurchaseOrderLine(
        purchase_order_id=purchase_order.id,
        description="Laptop computers",
        quantity=Decimal("2.000"),
        unit="EA",
        unit_price=Decimal("750.00"),
        total_amount=Decimal("1500.00"),
    )
    line_one.id = 801

    line_two = PurchaseOrderLine(
        purchase_order_id=purchase_order.id,
        description="Laptop bags",
        quantity=Decimal("2.000"),
        unit="EA",
        unit_price=Decimal("25.00"),
        total_amount=Decimal("50.00"),
    )
    line_two.id = 802

    purchase_order.supplier = supplier
    purchase_order.purchase_request = purchase_request
    purchase_order.lines = [
        line_one,
        line_two,
    ]

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


def test_executor_submits_finance_commitment_for_approved_purchase_order():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    integration_service = RecordingIntegrationService()

    executor = ProcurementFinancePostCommitExecutor(
        integration_service=integration_service,
        currency="usd",
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        context,
        result,
    )

    assert len(integration_service.requests) == 1

    request = integration_service.requests[0]

    assert request.provider == FINANCE_INTEGRATION_PROVIDER
    assert (
        request.operation
        == FINANCE_PROCUREMENT_COMMITMENT_OPERATION
    )

    payload = request.payload

    assert payload.purchase_order_reference == "PO-2026-0001"
    assert payload.purchase_request_reference == "PR-2026-0001"
    assert payload.supplier_reference == "SUP-001"

    assert payload.purchase_order_date == datetime(
        2026,
        9,
        15,
        tzinfo=timezone.utc,
    )

    assert payload.approved_at == datetime(
        2026,
        9,
        20,
        14,
        30,
        tzinfo=timezone.utc,
    )

    assert payload.currency == "USD"
    assert payload.total_procurement_value == Decimal(
        "1550.00"
    )

    assert len(payload.purchase_order_lines) == 2

    first_line = payload.purchase_order_lines[0]

    assert first_line.purchase_order_line_reference == "801"
    assert first_line.description == "Laptop computers"
    assert first_line.quantity == Decimal("2.000")
    assert first_line.unit == "EA"
    assert first_line.unit_price == Decimal("750.00")
    assert first_line.line_amount == Decimal("1500.00")

    second_line = payload.purchase_order_lines[1]

    assert second_line.purchase_order_line_reference == "802"
    assert second_line.description == "Laptop bags"
    assert second_line.quantity == Decimal("2.000")
    assert second_line.unit == "EA"
    assert second_line.unit_price == Decimal("25.00")
    assert second_line.line_amount == Decimal("50.00")

    assert payload.idempotency_key == (
        "procurement-commitment:PO-2026-0001"
    )


def test_executor_sets_procurement_context_metadata_on_integration_request():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    integration_service = RecordingIntegrationService()

    executor = ProcurementFinancePostCommitExecutor(
        integration_service=integration_service,
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        context,
        result,
    )

    request = integration_service.requests[0]

    assert request.metadata["module"] == "PROCUREMENT"
    assert (
        request.metadata["purchase_order_id"]
        == purchase_order.id
    )
    assert (
        request.metadata["purchase_order_reference"]
        == "PO-2026-0001"
    )
    assert (
        request.metadata["operation"]
        == context.operation
    )
    assert request.metadata["subject"] == context.user_id


def test_executor_ignores_non_approval_commands():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    integration_service = RecordingIntegrationService()

    executor = ProcurementFinancePostCommitExecutor(
        integration_service=integration_service,
    )

    executor.execute(
        object(),
        context,
        result,
    )

    assert integration_service.requests == []


def test_executor_ignores_unsuccessful_approval_result():
    purchase_order = build_purchase_order()

    result = ExecutionResult.failure_result(
        message="Purchase Order approval failed.",
    )

    integration_service = RecordingIntegrationService()

    executor = ProcurementFinancePostCommitExecutor(
        integration_service=integration_service,
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        build_context(),
        result,
    )

    assert integration_service.requests == []


def test_executor_requires_approval_timestamp():
    purchase_order = build_purchase_order()

    result = ExecutionResult.success_result(
        data=purchase_order,
        metadata={
            "purchase_order_id": purchase_order.id,
            "new_status": "APPROVED",
        },
    )

    integration_service = RecordingIntegrationService()

    executor = ProcurementFinancePostCommitExecutor(
        integration_service=integration_service,
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
