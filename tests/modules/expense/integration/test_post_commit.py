"""
Tests for the Expense → Catering post-commit executor.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.core.execution.context import ExecutionContext
from app.core.execution.results import ExecutionResult
from app.core.integration import (
    IntegrationResult,
    IntegrationResponse,
    IntegrationService,
)
from app.modules.catering.integration import (
    CATERING_CONSUME_APPROVED_EXPENSE_OPERATION,
    CATERING_INTEGRATION_PROVIDER,
)
from app.modules.catering.models import (
    CateringExpenseCostAssociation,
)
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.expense.commands import (
    ApproveExpenseCommand,
    SubmitExpenseCommand,
)
from app.modules.expense.integration import (
    ExpenseCateringPostCommitExecutor,
)
from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)


def _expense() -> Expense:
    classification = ExpenseClassification(
        name="Catering Supplies",
        code="CAT-SUP",
        description="Catering supplies",
        is_active=True,
    )

    expense = Expense(
        classification=classification,
        description="Catering food supplies",
        amount=Decimal("125.50"),
        expense_date=date(2026, 9, 28),
        status="APPROVED",
    )
    expense.id = 42
    expense.approved_at = datetime(
        2026,
        9,
        28,
        10,
        30,
        tzinfo=timezone.utc,
    )

    return expense


def _association(
    *,
    expense_id: int = 42,
    context_type: str = "EVENT",
    context_reference: str = "EVENT-001",
    contribution_id: str = "expense-42-event-001",
) -> CateringExpenseCostAssociation:
    association = CateringExpenseCostAssociation(
        expense_id=expense_id,
        catering_context_type=context_type,
        catering_context_reference=context_reference,
        status="ELIGIBLE",
        contribution_id=contribution_id,
    )
    association.id = 1
    return association


def _context() -> ExecutionContext:
    return ExecutionContext(
        user_id=7,
        operation="expense.approve",
    )


def _success_result(
    expense: Expense,
) -> ExecutionResult:
    return ExecutionResult.success_result(
        data=expense,
        metadata={
            "expense_id": expense.id,
            "previous_status": "SUBMITTED",
            "new_status": "APPROVED",
            "approved_at": expense.approved_at,
            "operation": "expense.approve",
        },
    )


def _integration_success() -> IntegrationResult:
    request = MagicMock()
    response = IntegrationResponse(
        success=True,
        data=MagicMock(),
    )

    return IntegrationResult(
        request=request,
        response=response,
    )


def _integration_failure() -> IntegrationResult:
    request = MagicMock()
    response = IntegrationResponse(
        success=False,
        message="Catering consumption failed.",
        error="CATERING_EXPENSE_CONSUMPTION_FAILED",
    )

    return IntegrationResult(
        request=request,
        response=response,
    )


def test_ignores_non_approval_commands():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )
    integration = MagicMock(
        spec=IntegrationService
    )

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    executor.execute(
        SubmitExpenseCommand(42),
        _context(),
        _success_result(_expense()),
    )

    repository.get_eligible_by_expense_id.assert_not_called()
    integration.execute.assert_not_called()


def test_ignores_unsuccessful_approval_result():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )
    integration = MagicMock(
        spec=IntegrationService
    )

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    result = ExecutionResult.failure_result(
        message="Invalid Expense state.",
        error_code="INVALID_EXPENSE_STATE",
        data=_expense(),
    )

    executor.execute(
        ApproveExpenseCommand(42),
        _context(),
        result,
    )

    repository.get_eligible_by_expense_id.assert_not_called()
    integration.execute.assert_not_called()


def test_requires_execution_context():
    executor = ExpenseCateringPostCommitExecutor(
        association_repository=MagicMock(
            spec=CateringExpenseCostAssociationRepository
        ),
        integration_service=MagicMock(
            spec=IntegrationService
        ),
    )

    with pytest.raises(TypeError):
        executor.execute(
            ApproveExpenseCommand(42),
            object(),
            _success_result(_expense()),
        )


def test_requires_execution_result():
    executor = ExpenseCateringPostCommitExecutor(
        association_repository=MagicMock(
            spec=CateringExpenseCostAssociationRepository
        ),
        integration_service=MagicMock(
            spec=IntegrationService
        ),
    )

    with pytest.raises(TypeError):
        executor.execute(
            ApproveExpenseCommand(42),
            _context(),
            object(),
        )


def test_requires_expense_result_data():
    executor = ExpenseCateringPostCommitExecutor(
        association_repository=MagicMock(
            spec=CateringExpenseCostAssociationRepository
        ),
        integration_service=MagicMock(
            spec=IntegrationService
        ),
    )

    result = ExecutionResult.success_result(
        data=object(),
        metadata={
            "approved_at": datetime.now(timezone.utc),
        },
    )

    with pytest.raises(TypeError):
        executor.execute(
            ApproveExpenseCommand(42),
            _context(),
            result,
        )


def test_requires_approval_timestamp():
    executor = ExpenseCateringPostCommitExecutor(
        association_repository=MagicMock(
            spec=CateringExpenseCostAssociationRepository
        ),
        integration_service=MagicMock(
            spec=IntegrationService
        ),
    )

    result = ExecutionResult.success_result(
        data=_expense(),
        metadata={},
    )

    with pytest.raises(ValueError):
        executor.execute(
            ApproveExpenseCommand(42),
            _context(),
            result,
        )


def test_no_eligible_associations_performs_no_delivery():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )
    repository.get_eligible_by_expense_id.return_value = []

    integration = MagicMock(
        spec=IntegrationService
    )

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    executor.execute(
        ApproveExpenseCommand(42),
        _context(),
        _success_result(_expense()),
    )

    repository.get_eligible_by_expense_id.assert_called_once_with(
        42
    )
    integration.execute.assert_not_called()


def test_delivers_all_eligible_associations():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )

    first = _association(
        context_reference="EVENT-001",
        contribution_id="expense-42-event-001",
    )
    second = _association(
        context_reference="EVENT-002",
        contribution_id="expense-42-event-002",
    )

    repository.get_eligible_by_expense_id.return_value = [
        first,
        second,
    ]

    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.return_value = _integration_success()

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    executor.execute(
        ApproveExpenseCommand(42),
        _context(),
        _success_result(_expense()),
    )

    assert integration.execute.call_count == 2

    first_request = integration.execute.call_args_list[0].args[0]
    second_request = integration.execute.call_args_list[1].args[0]

    assert first_request.provider == (
        CATERING_INTEGRATION_PROVIDER
    )
    assert first_request.operation == (
        CATERING_CONSUME_APPROVED_EXPENSE_OPERATION
    )

    assert first_request.payload.contribution_id == (
        "expense-42-event-001"
    )
    assert second_request.payload.contribution_id == (
        "expense-42-event-002"
    )


def test_builds_correct_immutable_contribution():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )

    association = _association()

    repository.get_eligible_by_expense_id.return_value = [
        association
    ]

    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.return_value = _integration_success()

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    expense = _expense()

    executor.execute(
        ApproveExpenseCommand(42),
        _context(),
        _success_result(expense),
    )

    request = integration.execute.call_args.args[0]
    contribution = request.payload

    assert contribution.expense_id == 42
    assert contribution.description == (
        "Catering food supplies"
    )
    assert contribution.amount == Decimal("125.50")
    assert contribution.expense_date == date(2026, 9, 28)
    assert contribution.classification_reference == "CAT-SUP"
    assert contribution.catering_context_type == "EVENT"
    assert contribution.catering_context_reference == "EVENT-001"
    assert contribution.approved_at == expense.approved_at
    assert contribution.contribution_id == (
        "expense-42-event-001"
    )

    with pytest.raises(
        AttributeError
    ):
        contribution.amount = Decimal("200.00")


def test_failed_integration_leaves_association_eligible():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )

    association = _association()

    repository.get_eligible_by_expense_id.return_value = [
        association
    ]

    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.return_value = _integration_failure()

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    with pytest.raises(RuntimeError):
        executor.execute(
            ApproveExpenseCommand(42),
            _context(),
            _success_result(_expense()),
        )

    assert association.status == "ELIGIBLE"
    assert association.consumed_at is None


def test_failure_in_one_association_does_not_prevent_other_delivery():
    repository = MagicMock(
        spec=CateringExpenseCostAssociationRepository
    )

    first = _association(
        context_reference="EVENT-001",
        contribution_id="expense-42-event-001",
    )
    second = _association(
        context_reference="EVENT-002",
        contribution_id="expense-42-event-002",
    )

    repository.get_eligible_by_expense_id.return_value = [
        first,
        second,
    ]

    integration = MagicMock(
        spec=IntegrationService
    )
    integration.execute.side_effect = [
        _integration_failure(),
        _integration_success(),
    ]

    executor = ExpenseCateringPostCommitExecutor(
        association_repository=repository,
        integration_service=integration,
    )

    with pytest.raises(RuntimeError):
        executor.execute(
            ApproveExpenseCommand(42),
            _context(),
            _success_result(_expense()),
        )

    assert integration.execute.call_count == 2
    assert first.status == "ELIGIBLE"
    assert second.status == "ELIGIBLE"
