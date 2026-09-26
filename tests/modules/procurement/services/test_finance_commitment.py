"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Finance commitment service tests.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.integration.exceptions import (
    IntegrationDeliveryException,
)
from app.core.integration.lifecycle import IntegrationLifecycle
from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
)
from app.modules.procurement.models import (
    ProcurementFinanceCommitment,
    PurchaseOrder,
)
from app.modules.procurement.services.finance_commitment import (
    ProcurementFinanceCommitmentService,
)


@pytest.fixture
def repository():
    return MagicMock()


@pytest.fixture
def lifecycle():
    return MagicMock(spec=IntegrationLifecycle)


@pytest.fixture
def service(repository, lifecycle):
    return ProcurementFinanceCommitmentService(
        repository=repository,
        integration_lifecycle=lifecycle,
    )


@pytest.fixture
def purchase_order():
    purchase_order = MagicMock(spec=PurchaseOrder)

    purchase_order.id = 101
    purchase_order.reference = "PO-2026-001"
    purchase_order.status = "APPROVED"
    purchase_order.order_date = datetime(2026, 9, 26)

    purchase_order.purchase_request = SimpleNamespace(
        reference="PR-2026-001",
    )

    purchase_order.supplier = SimpleNamespace(
        code="SUP-001",
        reference="SUP-001",
    )

    purchase_order.lines = (
        SimpleNamespace(
            id=1001,
            description="Office supplies",
            quantity=Decimal("10"),
            unit="EA",
            unit_price=Decimal("150.00"),
            total_amount=Decimal("1500.00"),
        ),
    )

    purchase_order.total_amount = Decimal("1500.00")

    return purchase_order


@pytest.fixture
def commitment(purchase_order):
    return ProcurementFinanceCommitment(
        id=1,
        purchase_order_id=purchase_order.id,
        purchase_order_reference=purchase_order.reference,
        idempotency_key=(
            "procurement-commitment:"
            f"{purchase_order.reference}"
        ),
        status="PENDING",
        attempt_count=0,
    )


def _successful_result(request: IntegrationRequest) -> IntegrationResult:
    response = IntegrationResponse(
        success=True,
        status_code=200,
        message="Finance commitment accepted.",
        request_id=request.request_id,
    )

    return IntegrationResult(
        request=request,
        response=response,
        duration_ms=25.0,
        provider=request.provider,
        operation=request.operation,
    )


def _rejected_result(request: IntegrationRequest) -> IntegrationResult:
    response = IntegrationResponse(
        success=False,
        status_code=422,
        message="Finance rejected the commitment.",
        error="BUSINESS_RULE_REJECTION",
        request_id=request.request_id,
    )

    return IntegrationResult(
        request=request,
        response=response,
        duration_ms=20.0,
        provider=request.provider,
        operation=request.operation,
    )


def test_register_creates_pending_commitment(
    service,
    repository,
    purchase_order,
):
    repository.get_by_idempotency_key.return_value = None
    repository.get_by_purchase_order_id.return_value = None
    repository.add.side_effect = lambda entity: entity

    result = service.register(purchase_order)

    assert isinstance(result, ProcurementFinanceCommitment)
    assert result.purchase_order_id == purchase_order.id
    assert result.purchase_order_reference == purchase_order.reference
    assert (
        result.idempotency_key
        == "procurement-commitment:PO-2026-001"
    )
    assert result.status == "PENDING"
    assert result.attempt_count == 0

    repository.add.assert_called_once_with(result)


def test_register_is_idempotent_for_existing_key(
    service,
    repository,
    purchase_order,
    commitment,
):
    repository.get_by_idempotency_key.return_value = commitment

    result = service.register(purchase_order)

    assert result is commitment
    repository.get_by_idempotency_key.assert_called_once_with(
        "procurement-commitment:PO-2026-001"
    )
    repository.add.assert_not_called()


def test_register_reuses_existing_commitment_for_purchase_order(
    service,
    repository,
    purchase_order,
    commitment,
):
    repository.get_by_idempotency_key.return_value = None
    repository.get_by_purchase_order_id.return_value = commitment

    result = service.register(purchase_order)

    assert result is commitment
    repository.add.assert_not_called()


def test_idempotency_key_is_deterministic(
    service,
    purchase_order,
):
    first_key = service.idempotency_key(purchase_order)
    second_key = service.idempotency_key(purchase_order)

    assert first_key == second_key
    assert first_key == "procurement-commitment:PO-2026-001"


def test_delivery_success_commits_commitment(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    approved_at = datetime(
        2026,
        9,
        26,
        10,
        30,
        0,
        tzinfo=timezone.utc,
    )

    repository.update.side_effect = lambda entity: entity
    lifecycle.execute.side_effect = (
        lambda request, subject=None:
        _successful_result(request)
    )

    result = service.deliver(
        commitment,
        purchase_order,
        approved_at=approved_at,
        subject=7,
    )

    assert isinstance(result, IntegrationResult)
    assert commitment.status == "COMMITTED"
    assert commitment.attempt_count == 1
    assert commitment.committed_at is not None
    assert commitment.last_failure_at is None
    assert commitment.next_retry_at is None
    assert commitment.last_error is None
    assert commitment.last_response_message == (
        "Finance commitment accepted."
    )
    assert commitment.last_response_status_code == 200

    lifecycle.execute.assert_called_once()

    request = lifecycle.execute.call_args.args[0]

    assert isinstance(request, IntegrationRequest)
    assert request.provider == "finance"
    assert request.operation == "procurement_commitment"
    assert (
        request.payload.idempotency_key
        == commitment.idempotency_key
    )

    assert request.payload.approved_at == approved_at
    assert request.metadata["idempotency_key"] == (
        commitment.idempotency_key
    )

    repository.update.assert_called()


def test_delivery_provider_rejection_is_terminal(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    approved_at = datetime(2026, 9, 26, 10, 30, 0)

    repository.update.side_effect = lambda entity: entity
    lifecycle.execute.side_effect = (
        lambda request, subject=None:
        _rejected_result(request)
    )

    result = service.deliver(
        commitment,
        purchase_order,
        approved_at=approved_at,
    )

    assert isinstance(result, IntegrationResult)
    assert commitment.status == "REJECTED"
    assert commitment.attempt_count == 1
    assert commitment.committed_at is None
    assert commitment.next_retry_at is None
    assert commitment.last_failure_at is None
    assert commitment.last_response_message == (
        "Finance rejected the commitment."
    )
    assert commitment.last_response_status_code == 422


def test_delivery_failure_becomes_retryable_failure(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    approved_at = datetime(2026, 9, 26, 10, 30, 0)

    repository.update.side_effect = lambda entity: entity

    lifecycle.execute.side_effect = IntegrationDeliveryException(
        "Finance provider unavailable."
    )

    with pytest.raises(IntegrationDeliveryException):
        service.deliver(
            commitment,
            purchase_order,
            approved_at=approved_at,
        )

    assert commitment.status == "RETRYABLE_FAILURE"
    assert commitment.attempt_count == 1
    assert commitment.last_attempted_at is not None
    assert commitment.last_failure_at is not None
    assert commitment.next_retry_at is not None
    assert commitment.last_error == (
        "Finance provider unavailable."
    )
    assert commitment.committed_at is None


def test_retry_eligibility_requires_retryable_failure(
    service,
    commitment,
):
    commitment.status = "PENDING"
    commitment.next_retry_at = None

    assert service.is_retry_eligible(commitment) is False

    commitment.status = "COMMITTED"
    commitment.next_retry_at = datetime.utcnow()

    assert service.is_retry_eligible(commitment) is False


def test_retry_eligibility_requires_due_retry_time(
    service,
    commitment,
):
    commitment.status = "RETRYABLE_FAILURE"

    commitment.next_retry_at = (
        datetime.utcnow() + timedelta(minutes=10)
    )

    assert service.is_retry_eligible(commitment) is False

    commitment.next_retry_at = (
        datetime.utcnow() - timedelta(minutes=1)
    )

    assert service.is_retry_eligible(commitment) is True


def test_retry_reuses_business_idempotency_key_but_creates_new_request_id(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    approved_at = datetime(2026, 9, 26, 10, 30, 0)

    repository.update.side_effect = lambda entity: entity

    lifecycle.execute.side_effect = (
        lambda request, subject=None:
        _successful_result(request)
    )

    commitment.status = "RETRYABLE_FAILURE"
    commitment.next_retry_at = (
        datetime.utcnow() - timedelta(minutes=1)
    )
    commitment.attempt_count = 1

    result = service.retry(
        commitment,
        purchase_order,
        approved_at=approved_at,
    )

    assert isinstance(result, IntegrationResult)
    assert commitment.status == "COMMITTED"
    assert commitment.attempt_count == 2

    request = lifecycle.execute.call_args.args[0]

    assert (
        request.payload.idempotency_key
        == commitment.idempotency_key
    )


def test_committed_commitment_cannot_be_delivered_again(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    commitment.status = "COMMITTED"

    with pytest.raises(ValueError):
        service.deliver(
            commitment,
            purchase_order,
            approved_at=datetime(2026, 9, 26, 10, 30, 0),
        )

    lifecycle.execute.assert_not_called()
    repository.update.assert_not_called()


def test_rejected_commitment_cannot_be_retried(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    commitment.status = "REJECTED"

    with pytest.raises(ValueError):
        service.retry(
            commitment,
            purchase_order,
            approved_at=datetime(2026, 9, 26, 10, 30, 0),
        )

    lifecycle.execute.assert_not_called()
    repository.update.assert_not_called()


def test_delivery_increments_attempt_count_before_integration(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    approved_at = datetime(2026, 9, 26, 10, 30, 0)

    repository.update.side_effect = lambda entity: entity
    lifecycle.execute.side_effect = (
        lambda request, subject=None:
        _successful_result(request)
    )

    service.deliver(
        commitment,
        purchase_order,
        approved_at=approved_at,
    )

    assert commitment.attempt_count == 1
    assert commitment.last_attempted_at is not None


def test_retry_keeps_same_idempotency_key_across_attempts(
    service,
    repository,
    lifecycle,
    purchase_order,
    commitment,
):
    approved_at = datetime(2026, 9, 26, 10, 30, 0)

    repository.update.side_effect = lambda entity: entity

    requests = []

    def execute(request, subject=None):
        requests.append(request)
        if len(requests) == 1:
            raise IntegrationDeliveryException(
                "Temporary Finance outage."
            )
        return _successful_result(request)

    lifecycle.execute.side_effect = execute

    with pytest.raises(IntegrationDeliveryException):
        service.deliver(
            commitment,
            purchase_order,
            approved_at=approved_at,
        )

    commitment.next_retry_at = (
        datetime.utcnow() - timedelta(minutes=1)
    )

    service.retry(
        commitment,
        purchase_order,
        approved_at=approved_at,
    )

    assert len(requests) == 2

    assert (
        requests[0].payload.idempotency_key
        == requests[1].payload.idempotency_key
        == commitment.idempotency_key
    )

    assert (
        requests[0].request_id
        != requests[1].request_id
    )
