"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Finance Integration

Finance provider integration with the enterprise IntegrationService.
"""

from datetime import datetime, timezone
from decimal import Decimal

from app.core.integration import (
    IntegrationProviderRegistry,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationService,
)
from app.modules.procurement.integration import (
    FINANCE_INTEGRATION_PROVIDER,
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
    ProcurementFinancialEffectLine,
    ProcurementFinancialEffectRequest,
)
from app.modules.procurement.integration.providers.finance import (
    FinanceProcurementIntegrationProvider,
)


def build_line():
    return ProcurementFinancialEffectLine(
        purchase_order_line_reference="POL-001",
        description="Office chairs",
        quantity=Decimal("10.000"),
        unit="each",
        unit_price=Decimal("125.00"),
        line_amount=Decimal("1250.00"),
    )


def build_payload():
    return ProcurementFinancialEffectRequest(
        purchase_order_reference="PO-001",
        purchase_request_reference="PR-001",
        supplier_reference="SUP-001",
        purchase_order_date=datetime(
            2026,
            9,
            25,
            9,
            0,
            tzinfo=timezone.utc,
        ),
        approved_at=datetime(
            2026,
            9,
            25,
            10,
            0,
            tzinfo=timezone.utc,
        ),
        currency="USD",
        total_procurement_value=Decimal("1250.00"),
        purchase_order_lines=(build_line(),),
        idempotency_key="procurement-commitment:PO-001",
    )


def build_request():
    return IntegrationRequest(
        provider=FINANCE_INTEGRATION_PROVIDER,
        operation=FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
        payload=build_payload(),
        metadata={
            "module": "PROCUREMENT",
            "purchase_order_reference": "PO-001",
            "operation": "procurement.purchase_order.approve",
            "subject": "test-user",
        },
    )


def build_service():
    provider = FinanceProcurementIntegrationProvider()

    registry = IntegrationProviderRegistry()
    registry.register(provider)

    service = IntegrationService(
        provider_registry=registry
    )

    return service


def test_finance_provider_executes_through_integration_service():
    service = build_service()
    request = build_request()

    result = service.execute(request)

    assert result.success is False
    assert result.failed is True

    assert result.provider == (
        FINANCE_INTEGRATION_PROVIDER
    )

    assert result.operation == (
        FINANCE_PROCUREMENT_COMMITMENT_OPERATION
    )

    assert isinstance(
        result.response,
        IntegrationResponse,
    )

    assert result.response.success is False
    assert result.response.error == (
        "FINANCE_PROCESSING_NOT_IMPLEMENTED"
    )

    assert result.response.request_id == (
        request.request_id
    )


def test_finance_provider_is_registered_under_expected_identity():
    service = build_service()

    assert service.has_provider(
        FINANCE_INTEGRATION_PROVIDER
    ) is True

    assert service.provider_count() == 1


def test_finance_provider_is_resolved_by_operation():
    service = build_service()
    request = build_request()

    result = service.execute(request)

    assert result.provider == "finance"
    assert result.operation == "procurement_commitment"


def test_finance_integration_preserves_request_identity():
    service = build_service()
    request = build_request()

    result = service.execute(request)

    assert result.request is request
    assert result.response.request_id == request.request_id


def test_finance_provider_does_not_require_finance_persistence():
    service = build_service()
    request = build_request()

    result = service.execute(request)

    assert result.response.error == (
        "FINANCE_PROCESSING_NOT_IMPLEMENTED"
    )
