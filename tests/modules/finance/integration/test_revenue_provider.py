"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Tests for the Finance Revenue integration provider.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.core.integration import (
    IntegrationRequest,
)
from app.modules.catering.integration import (
    CateringRevenueContribution,
)
from app.modules.finance.integration import (
    FINANCE_CATERING_REVENUE_OPERATION,
    FINANCE_INTEGRATION_PROVIDER,
)
from app.modules.finance.integration.providers import (
    FinanceRevenueIntegrationProvider,
)
from app.modules.finance.models import FinanceRevenue
from app.modules.finance.workflows import FinanceRevenueWorkflow


def build_contribution():
    return CateringRevenueContribution(
        revenue_reference="CAT-REV-001",
        source_type="catering_event",
        source_reference="EVENT-001",
        amount=Decimal("1250.00"),
        currency="USD",
        revenue_date=date(2026, 9, 29),
        revenue_classification="CATERING",
        contribution_id="catering-revenue:CAT-REV-001",
    )


def build_request(**overrides):
    values = {
        "provider": FINANCE_INTEGRATION_PROVIDER,
        "operation": FINANCE_CATERING_REVENUE_OPERATION,
        "payload": build_contribution(),
    }
    values.update(overrides)

    return IntegrationRequest(**values)


def build_finance_revenue():
    return FinanceRevenue(
        revenue_reference="CAT-REV-001",
        contribution_reference="catering-revenue:CAT-REV-001",
        source_type="catering_event",
        source_reference="EVENT-001",
        amount=Decimal("1250.00"),
        currency="USD",
        revenue_date=date(2026, 9, 29),
        revenue_classification="CATERING",
        status=FinanceRevenueWorkflow.PENDING,
    )


def build_provider():
    revenue_service = Mock()
    revenue_service.consume_contribution.return_value = (
        build_finance_revenue()
    )

    return (
        FinanceRevenueIntegrationProvider(
            revenue_service=revenue_service,
        ),
        revenue_service,
    )


def test_provider_identity():
    provider = FinanceRevenueIntegrationProvider()

    assert provider.provider_name == "finance"
    assert (
        provider.provider_name
        == FINANCE_INTEGRATION_PROVIDER
    )


def test_provider_supports_catering_revenue_operation():
    provider = FinanceRevenueIntegrationProvider()

    assert provider.supports(
        FINANCE_CATERING_REVENUE_OPERATION
    )


def test_provider_rejects_unsupported_operation():
    provider = FinanceRevenueIntegrationProvider()

    assert not provider.supports(
        "unsupported_operation"
    )


def test_provider_validates_valid_catering_revenue_request():
    provider = FinanceRevenueIntegrationProvider()

    provider.validate(
        build_request()
    )


def test_provider_rejects_invalid_payload_type():
    provider = FinanceRevenueIntegrationProvider()

    response = provider.execute(
        build_request(
            payload={
                "revenue_reference": "CAT-REV-001"
            }
        )
    )

    assert response.success is False
    assert response.error == (
        "INVALID_FINANCE_CATERING_REVENUE"
    )


def test_provider_rejects_unsupported_operation():
    provider = FinanceRevenueIntegrationProvider()

    response = provider.execute(
        build_request(
            operation="unsupported_operation"
        )
    )

    assert response.success is False
    assert response.error == (
        "INVALID_FINANCE_CATERING_REVENUE"
    )


def test_provider_consumes_revenue_into_finance():
    provider, revenue_service = build_provider()

    response = provider.execute(
        build_request()
    )

    assert response.success is True
    assert response.request_id is not None
    assert response.data["revenue_reference"] == (
        "CAT-REV-001"
    )
    assert response.data["contribution_reference"] == (
        "catering-revenue:CAT-REV-001"
    )
    assert response.data["status"] == "PENDING"

    revenue_service.consume_contribution.assert_called_once()

    consumed_revenue = (
        revenue_service.consume_contribution.call_args.args[0]
    )

    assert consumed_revenue.revenue_reference == (
        "CAT-REV-001"
    )
    assert consumed_revenue.contribution_reference == (
        "catering-revenue:CAT-REV-001"
    )
    assert consumed_revenue.source_type == "catering_event"
    assert consumed_revenue.source_reference == "EVENT-001"
    assert consumed_revenue.amount == Decimal("1250.00")
    assert consumed_revenue.currency == "USD"
    assert consumed_revenue.revenue_date == date(2026, 9, 29)
    assert consumed_revenue.revenue_classification == "CATERING"
    assert consumed_revenue.status == FinanceRevenueWorkflow.PENDING


def test_provider_preserves_request_identity():
    provider, revenue_service = build_provider()
    request = build_request()

    response = provider.execute(request)

    assert response.request_id == request.request_id
    revenue_service.consume_contribution.assert_called_once()


def test_provider_does_not_expose_finance_repository():
    provider = FinanceRevenueIntegrationProvider()

    assert not hasattr(
        provider,
        "repository",
    )
    assert not hasattr(
        provider,
        "finance_repository",
    )


def test_provider_does_not_expose_accounting_operations():
    provider = FinanceRevenueIntegrationProvider()

    assert not provider.supports("post_journal")
    assert not provider.supports("create_invoice")
    assert not provider.supports("process_payment")
    assert not provider.supports("settle_supplier")
