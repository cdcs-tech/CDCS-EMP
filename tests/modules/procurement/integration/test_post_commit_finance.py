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
from app.core.integration.audit import IntegrationAuditHook
from app.core.integration.event_hook import IntegrationEventHook
from app.core.integration.lifecycle import IntegrationLifecycle
from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResponse,
)
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
    and returns the configured IntegrationResponse through
    the normal IntegrationService contract.
    """

    def __init__(
        self,
        response: IntegrationResponse,
    ) -> None:
        super().__init__()
        self.requests: list[IntegrationRequest] = []
        self.response = response

    def execute(
        self,
        request: IntegrationRequest,
    ):
        self.requests.append(request)

        from app.core.integration.models import IntegrationResult

        return IntegrationResult(
            request=request,
            response=self.response,
            duration_ms=1.0,
            provider=request.provider,
            operation=request.operation,
        )


class RecordingIntegrationEventHook(IntegrationEventHook):
    """
    Integration event hook test double.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests = []
        self.results = []
        self.failures = []

    def publish_request(
        self,
        request: IntegrationRequest,
        subject: str | None = None,
    ) -> None:
        self.requests.append(
            (request, subject)
        )

    def publish_result(
        self,
        result,
        subject: str | None = None,
    ) -> None:
        self.results.append(
            (result, subject)
        )

    def publish_failure(
        self,
        request: IntegrationRequest,
        message: str,
        subject: str | None = None,
        metadata=None,
    ) -> None:
        self.failures.append(
            (
                request,
                message,
                subject,
                metadata,
            )
        )


class RecordingIntegrationAuditHook(IntegrationAuditHook):
    """
    Integration audit hook test double.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests = []
        self.results = []
        self.failures = []

    def record_request(
        self,
        request: IntegrationRequest,
        subject: str | None = None,
    ) -> None:
        self.requests.append(
            (request, subject)
        )

    def record_result(
        self,
        result,
        subject: str | None = None,
    ) -> None:
        self.results.append(
            (result, subject)
        )

    def record_failure(
        self,
        request: IntegrationRequest,
        message: str,
        subject: str | None = None,
        metadata=None,
    ) -> None:
        self.failures.append(
            (
                request,
                message,
                subject,
                metadata,
            )
        )


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


def build_lifecycle(
    response: IntegrationResponse,
):
    service = RecordingIntegrationService(
        response=response,
    )
    event_hook = RecordingIntegrationEventHook()
    audit_hook = RecordingIntegrationAuditHook()

    lifecycle = IntegrationLifecycle(
        service=service,
        event_hook=event_hook,
        audit_hook=audit_hook,
    )

    return (
        lifecycle,
        service,
        event_hook,
        audit_hook,
    )


def test_executor_submits_finance_commitment_for_approved_purchase_order():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    response = IntegrationResponse(
        success=True,
        status_code=200,
        data={"accepted": True},
        message="Finance commitment accepted.",
    )

    (
        lifecycle,
        integration_service,
        _event_hook,
        _audit_hook,
    ) = build_lifecycle(response)

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
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

    response = IntegrationResponse(
        success=True,
        status_code=200,
        message="Finance commitment accepted.",
    )

    (
        lifecycle,
        integration_service,
        _event_hook,
        _audit_hook,
    ) = build_lifecycle(response)

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
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

    response = IntegrationResponse(
        success=True,
        status_code=200,
        message="Finance commitment accepted.",
    )

    (
        lifecycle,
        integration_service,
        _event_hook,
        _audit_hook,
    ) = build_lifecycle(response)

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
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

    response = IntegrationResponse(
        success=True,
        status_code=200,
        message="Finance commitment accepted.",
    )

    (
        lifecycle,
        integration_service,
        _event_hook,
        _audit_hook,
    ) = build_lifecycle(response)

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
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

    response = IntegrationResponse(
        success=True,
        status_code=200,
        message="Finance commitment accepted.",
    )

    (
        lifecycle,
        _integration_service,
        _event_hook,
        _audit_hook,
    ) = build_lifecycle(response)

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
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


def test_executor_handles_provider_declared_finance_failure():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    response = IntegrationResponse(
        success=False,
        status_code=422,
        message="Finance commitment rejected.",
        error="Commitment validation failed.",
    )

    (
        lifecycle,
        integration_service,
        event_hook,
        audit_hook,
    ) = build_lifecycle(response)

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
    )

    executor.execute(
        ApprovePurchaseOrderCommand(
            purchase_order_id=purchase_order.id,
        ),
        context,
        result,
    )

    assert len(integration_service.requests) == 1

    assert len(event_hook.requests) == 1
    assert len(event_hook.results) == 1
    assert event_hook.failures == []

    integration_result = event_hook.results[0][0]

    assert integration_result.success is False
    assert integration_result.failed is True

    assert len(audit_hook.requests) == 1
    assert len(audit_hook.results) == 1
    assert audit_hook.failures == []

    audited_result = audit_hook.results[0][0]

    assert audited_result.success is False
    assert audited_result.failed is True


class FailingIntegrationService(IntegrationService):
    """
    IntegrationService test double that raises during delivery.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[IntegrationRequest] = []

    def execute(
        self,
        request: IntegrationRequest,
    ):
        self.requests.append(request)

        from app.core.integration.exceptions import (
            IntegrationDeliveryException,
        )

        raise IntegrationDeliveryException(
            "Finance provider unavailable."
        )


def test_executor_propagates_delivery_failure_from_lifecycle():
    purchase_order = build_purchase_order()
    context = build_context()
    result = build_success_result(purchase_order)

    service = FailingIntegrationService()
    event_hook = RecordingIntegrationEventHook()
    audit_hook = RecordingIntegrationAuditHook()

    lifecycle = IntegrationLifecycle(
        service=service,
        event_hook=event_hook,
        audit_hook=audit_hook,
    )

    executor = ProcurementFinancePostCommitExecutor(
        integration_lifecycle=lifecycle,
    )

    with pytest.raises(
        Exception,
        match="Finance provider unavailable",
    ):
        executor.execute(
            ApprovePurchaseOrderCommand(
                purchase_order_id=purchase_order.id,
            ),
            context,
            result,
        )

    assert len(service.requests) == 1

    assert len(event_hook.requests) == 1
    assert event_hook.results == []
    assert len(event_hook.failures) == 1

    failure_request, failure_message, subject, metadata = (
        event_hook.failures[0]
    )

    assert (
        failure_request
        is service.requests[0]
    )
    assert "Finance provider unavailable" in failure_message
    assert subject == context.user_id
    assert metadata is not None

    assert len(audit_hook.requests) == 1
    assert audit_hook.results == []
    assert len(audit_hook.failures) == 1

    (
        audit_request,
        audit_message,
        audit_subject,
        audit_metadata,
    ) = audit_hook.failures[0]

    assert (
        audit_request
        is service.requests[0]
    )
    assert "Finance provider unavailable" in audit_message
    assert audit_subject == context.user_id
    assert audit_metadata is not None
