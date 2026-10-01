from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.modules.catering.integration import (
    CATERING_CONSUME_APPROVED_EXPENSE_OPERATION,
    CATERING_INTEGRATION_PROVIDER,
    ApprovedExpenseCostContribution,
)
from app.modules.catering.integration.providers.expense import (
    CateringExpenseIntegrationProvider,
)
from app.modules.catering.models import (
    CateringExpenseCostAssociation,
)
from app.modules.catering.services import (
    CateringExpenseCostConsumptionService,
)


def _contribution(
    contribution_id: str = "expense-17-catering-event-1",
) -> ApprovedExpenseCostContribution:
    return ApprovedExpenseCostContribution(
        expense_id=17,
        description="Catering supplies",
        amount=Decimal("125.50"),
        expense_date=date(2026, 9, 30),
        classification_reference="CATERING_SUPPLIES",
        catering_context_type="EVENT",
        catering_context_reference="EVENT-1",
        approved_at=datetime(
            2026,
            9,
            30,
            12,
            30,
            tzinfo=timezone.utc,
        ),
        contribution_id=contribution_id,
    )


def _request(
    payload=None,
    operation=CATERING_CONSUME_APPROVED_EXPENSE_OPERATION,
) -> IntegrationRequest:
    return IntegrationRequest(
        provider=CATERING_INTEGRATION_PROVIDER,
        operation=operation,
        payload=payload if payload is not None else _contribution(),
    )


def test_provider_name():
    provider = CateringExpenseIntegrationProvider()

    assert provider.provider_name == CATERING_INTEGRATION_PROVIDER


def test_provider_supports_approved_expense_consumption():
    provider = CateringExpenseIntegrationProvider()

    assert provider.supports(
        CATERING_CONSUME_APPROVED_EXPENSE_OPERATION
    )


def test_provider_rejects_unknown_operation():
    provider = CateringExpenseIntegrationProvider()

    assert not provider.supports("unknown_operation")


def test_validate_requires_supported_operation():
    provider = CateringExpenseIntegrationProvider()

    request = _request(operation="unknown_operation")

    with pytest.raises(ValueError, match="Unsupported Catering integration operation"):
        provider.validate(request)


def test_validate_requires_expected_payload():
    provider = CateringExpenseIntegrationProvider()

    request = _request(payload={"expense_id": 17})

    with pytest.raises(
        TypeError,
        match="ApprovedExpenseCostContribution",
    ):
        provider.validate(request)


def test_execute_delegates_to_consumption_service():
    association = Mock(
        spec=CateringExpenseCostAssociation,
    )

    service = Mock(
        spec=CateringExpenseCostConsumptionService,
    )
    service.consume.return_value = association

    provider = CateringExpenseIntegrationProvider(
        consumption_service=service,
    )

    request = _request()

    response = provider.execute(request)

    assert isinstance(response, IntegrationResponse)
    assert response.success is True
    assert response.data is association
    assert response.request_id == request.request_id

    service.consume.assert_called_once_with(request.payload)


def test_execute_returns_validation_failure():
    provider = CateringExpenseIntegrationProvider()

    request = _request(payload={"invalid": True})

    response = provider.execute(request)

    assert response.success is False
    assert response.error == "INVALID_CATERING_EXPENSE_CONTRIBUTION"
    assert response.request_id == request.request_id


def test_execute_returns_consumption_failure():
    service = Mock(
        spec=CateringExpenseCostConsumptionService,
    )
    service.consume.side_effect = ValueError(
        "No eligible Catering Expense Cost Association"
    )

    provider = CateringExpenseIntegrationProvider(
        consumption_service=service,
    )

    request = _request()

    response = provider.execute(request)

    assert response.success is False
    assert response.error == "CATERING_EXPENSE_CONSUMPTION_FAILED"
    assert response.message == (
        "No eligible Catering Expense Cost Association"
    )
    assert response.request_id == request.request_id


def test_provider_requires_consumption_service():
    provider = CateringExpenseIntegrationProvider()

    assert isinstance(
        provider.consumption_service,
        CateringExpenseCostConsumptionService,
    )
