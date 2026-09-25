from datetime import datetime, timezone
from decimal import Decimal

from app.core.integration import IntegrationRequest
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


def build_request(**overrides):
    values = {
        "provider": FINANCE_INTEGRATION_PROVIDER,
        "operation": FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
        "payload": build_payload(),
    }
    values.update(overrides)

    return IntegrationRequest(**values)


def test_provider_identity():
    provider = FinanceProcurementIntegrationProvider()

    assert provider.provider_name == "finance"
    assert provider.provider_name == FINANCE_INTEGRATION_PROVIDER


def test_provider_supports_procurement_commitment_operation():
    provider = FinanceProcurementIntegrationProvider()

    assert provider.supports(
        FINANCE_PROCUREMENT_COMMITMENT_OPERATION
    )


def test_provider_rejects_unsupported_operation():
    provider = FinanceProcurementIntegrationProvider()

    assert not provider.supports("unknown_operation")


def test_provider_validates_valid_procurement_commitment_request():
    provider = FinanceProcurementIntegrationProvider()
    request = build_request()

    provider.validate(request)


def test_provider_rejects_invalid_payload_type():
    provider = FinanceProcurementIntegrationProvider()

    request = build_request(payload={"purchase_order_reference": "PO-001"})

    response = provider.execute(request)

    assert response.success is False
    assert response.error == (
        "INVALID_FINANCE_PROCUREMENT_COMMITMENT"
    )


def test_provider_rejects_unsupported_operation():
    provider = FinanceProcurementIntegrationProvider()

    request = build_request(
        operation="unsupported_operation",
    )

    response = provider.execute(request)

    assert response.success is False
    assert response.error == (
        "INVALID_FINANCE_PROCUREMENT_COMMITMENT"
    )


def test_provider_execute_does_not_claim_finance_processing_is_complete():
    provider = FinanceProcurementIntegrationProvider()
    request = build_request()

    response = provider.execute(request)

    assert response.success is False
    assert response.error == "FINANCE_PROCESSING_NOT_IMPLEMENTED"
    assert (
        response.message
        == "Finance procurement commitment processing is "
        "not implemented."
    )
    assert response.request_id == request.request_id


def test_provider_does_not_mutate_procurement_payload():
    provider = FinanceProcurementIntegrationProvider()
    payload = build_payload()

    request = IntegrationRequest(
        provider=FINANCE_INTEGRATION_PROVIDER,
        operation=FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
        payload=payload,
    )

    provider.execute(request)

    assert payload.purchase_order_reference == "PO-001"
    assert payload.supplier_reference == "SUP-001"
    assert payload.total_procurement_value == Decimal("1250.00")


def test_provider_has_no_finance_persistence_boundary():
    provider = FinanceProcurementIntegrationProvider()

    assert not hasattr(provider, "repository")
    assert not hasattr(provider, "finance_repository")
    assert not hasattr(provider, "ledger_repository")


def test_provider_does_not_expose_accounting_operations():
    provider = FinanceProcurementIntegrationProvider()

    assert not provider.supports("post_journal")
    assert not provider.supports("create_invoice")
    assert not provider.supports("process_payment")
    assert not provider.supports("settle_supplier")
