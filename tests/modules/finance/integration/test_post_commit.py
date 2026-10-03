from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.core.execution.context import (
    ExecutionContext,
)
from app.core.execution.results import (
    ExecutionResult,
)
from app.core.integration.models import (
    IntegrationResponse,
)
from app.core.integration.service import (
    IntegrationService,
)
from app.modules.catering.commands import (
    RecognizeCateringRevenueCommand,
)
from app.modules.catering.models import (
    CateringRevenue,
)
from app.modules.finance.integration.post_commit import (
    FinanceCateringRevenuePostCommitExecutor,
)


def _revenue() -> CateringRevenue:
    return CateringRevenue(
        id=42,
        revenue_reference="CAT-REV-00042",
        source_type="CATERING_EVENT",
        source_reference="EVENT-42",
        amount=Decimal("1250.00"),
        currency="USD",
        revenue_date=date(2026, 9, 30),
        revenue_classification="CATERING_SERVICE",
        status="RECOGNIZED",
    )


def _context() -> ExecutionContext:
    return ExecutionContext(
        user_id="7",
        module_name="CATERING",
        operation="catering.revenue.recognize",
    )


def _success_result(
    revenue: CateringRevenue,
) -> ExecutionResult:
    return ExecutionResult.success_result(
        data=revenue,
        message="Catering Revenue recognized.",
        metadata={
            "revenue_id": revenue.id,
            "previous_status": "ELIGIBLE",
            "new_status": "RECOGNIZED",
            "recognized_at": None,
            "operation": (
                "catering.revenue.recognize"
            ),
        },
    )


def _integration_success():
    return IntegrationResponse(
        success=True,
        status_code=200,
        data={
            "status": "PENDING",
        },
        message="Consumed.",
    )


def _integration_failure():
    return IntegrationResponse(
        success=False,
        status_code=500,
        data=None,
        message="Finance unavailable.",
    )


def test_ignores_unrelated_command():
    integration = MagicMock(
        spec=IntegrationService
    )

    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=integration
        )
    )

    executor.execute(
        object(),
        _context(),
        _success_result(_revenue()),
    )

    integration.execute.assert_not_called()


def test_ignores_unsuccessful_result():
    integration = MagicMock(
        spec=IntegrationService
    )

    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=integration
        )
    )

    result = ExecutionResult.failure_result(
        message="Recognition failed.",
        data=_revenue(),
    )

    executor.execute(
        RecognizeCateringRevenueCommand(42),
        _context(),
        result,
    )

    integration.execute.assert_not_called()


def test_requires_execution_context():
    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=MagicMock(
                spec=IntegrationService
            )
        )
    )

    with pytest.raises(TypeError):
        executor.execute(
            RecognizeCateringRevenueCommand(42),
            object(),
            _success_result(_revenue()),
        )


def test_requires_execution_result():
    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=MagicMock(
                spec=IntegrationService
            )
        )
    )

    with pytest.raises(TypeError):
        executor.execute(
            RecognizeCateringRevenueCommand(42),
            _context(),
            object(),
        )


def test_delivers_correct_finance_request():
    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.return_value = (
        _integration_success()
    )

    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=integration
        )
    )

    revenue = _revenue()

    executor.execute(
        RecognizeCateringRevenueCommand(42),
        _context(),
        _success_result(revenue),
    )

    integration.execute.assert_called_once()

    request = (
        integration.execute.call_args.args[0]
    )

    assert request.provider == "finance"
    assert (
        request.operation
        == "consume_catering_revenue"
    )

    contribution = request.payload

    assert (
        contribution.revenue_reference
        == "CAT-REV-00042"
    )
    assert (
        contribution.source_type
        == "CATERING_EVENT"
    )
    assert (
        contribution.source_reference
        == "EVENT-42"
    )
    assert contribution.amount == Decimal(
        "1250.00"
    )
    assert contribution.currency == "USD"
    assert (
        contribution.revenue_date
        == date(2026, 9, 30)
    )
    assert (
        contribution.revenue_classification
        == "CATERING_SERVICE"
    )
    assert (
        contribution.contribution_id
        == "CAT-REV-00042"
    )


def test_failed_finance_delivery_does_not_mutate_revenue():
    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.return_value = (
        _integration_failure()
    )

    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=integration
        )
    )

    revenue = _revenue()

    with pytest.raises(RuntimeError):
        executor.execute(
            RecognizeCateringRevenueCommand(42),
            _context(),
            _success_result(revenue),
        )

    assert revenue.status == "RECOGNIZED"
    assert (
        revenue.revenue_reference
        == "CAT-REV-00042"
    )
    assert revenue.amount == Decimal(
        "1250.00"
    )


def test_successful_finance_delivery_does_not_mutate_revenue():
    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.return_value = (
        _integration_success()
    )

    executor = (
        FinanceCateringRevenuePostCommitExecutor(
            integration_service=integration
        )
    )

    revenue = _revenue()

    original_status = revenue.status
    original_reference = revenue.revenue_reference
    original_amount = revenue.amount

    executor.execute(
        RecognizeCateringRevenueCommand(42),
        _context(),
        _success_result(revenue),
    )

    assert revenue.status == original_status
    assert (
        revenue.revenue_reference
        == original_reference
    )
    assert revenue.amount == original_amount
