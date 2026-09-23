"""
Tests for Expense workflow command handlers.
"""

from unittest.mock import Mock

from app.core.execution.context import ExecutionContext
from app.core.execution.results import ExecutionResult

from app.modules.expense.commands import (
    ApproveExpenseCommand,
    CloseExpenseCommand,
    RejectExpenseCommand,
    ResubmitExpenseCommand,
    ReturnExpenseCommand,
    SubmitExpenseCommand,
)
from app.modules.expense.handlers import (
    ApproveExpenseHandler,
    CloseExpenseHandler,
    RejectExpenseHandler,
    ResubmitExpenseHandler,
    ReturnExpenseHandler,
    SubmitExpenseHandler,
)


def _context(operation: str) -> ExecutionContext:
    return ExecutionContext(operation=operation)


def _expense(status: str, expense_id: int = 1):
    return Mock(id=expense_id, status=status)


def test_submit_handler_supports_submit_command():
    """
    SubmitExpenseHandler supports SubmitExpenseCommand.
    """

    handler = SubmitExpenseHandler(
        service=Mock()
    )

    assert handler.command_type is SubmitExpenseCommand


def test_approve_handler_supports_approve_command():
    """
    ApproveExpenseHandler supports ApproveExpenseCommand.
    """

    handler = ApproveExpenseHandler(
        service=Mock()
    )

    assert handler.command_type is ApproveExpenseCommand


def test_reject_handler_supports_reject_command():
    """
    RejectExpenseHandler supports RejectExpenseCommand.
    """

    handler = RejectExpenseHandler(
        service=Mock()
    )

    assert handler.command_type is RejectExpenseCommand


def test_return_handler_supports_return_command():
    """
    ReturnExpenseHandler supports ReturnExpenseCommand.
    """

    handler = ReturnExpenseHandler(
        service=Mock()
    )

    assert handler.command_type is ReturnExpenseCommand


def test_resubmit_handler_supports_resubmit_command():
    """
    ResubmitExpenseHandler supports ResubmitExpenseCommand.
    """

    handler = ResubmitExpenseHandler(
        service=Mock()
    )

    assert handler.command_type is ResubmitExpenseCommand


def test_close_handler_supports_close_command():
    """
    CloseExpenseHandler supports CloseExpenseCommand.
    """

    handler = CloseExpenseHandler(
        service=Mock()
    )

    assert handler.command_type is CloseExpenseCommand


def test_submit_handler_delegates_to_service():
    """
    SubmitExpenseHandler loads the Expense and delegates
    submission to ExpenseService.
    """

    expense = _expense("DRAFT")
    service = Mock()
    service.get.return_value = expense
    service.submit.return_value = expense

    handler = SubmitExpenseHandler(
        service=service
    )

    command = SubmitExpenseCommand(1)

    result = handler.handle(
        command,
        _context("expense.submit"),
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.data is expense

    service.get.assert_called_once_with(1)
    service.submit.assert_called_once_with(expense)


def test_approve_handler_delegates_to_service():
    """
    ApproveExpenseHandler loads the Expense and delegates
    approval to ExpenseService.
    """

    expense = _expense("SUBMITTED")
    service = Mock()
    service.get.return_value = expense
    service.approve.return_value = expense

    handler = ApproveExpenseHandler(
        service=service
    )

    command = ApproveExpenseCommand(1)

    result = handler.handle(
        command,
        _context("expense.approve"),
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.data is expense

    service.get.assert_called_once_with(1)
    service.approve.assert_called_once_with(expense)


def test_reject_handler_delegates_to_service():
    """
    RejectExpenseHandler loads the Expense and delegates
    rejection to ExpenseService.
    """

    expense = _expense("SUBMITTED")
    service = Mock()
    service.get.return_value = expense
    service.reject.return_value = expense

    handler = RejectExpenseHandler(
        service=service
    )

    command = RejectExpenseCommand(1)

    result = handler.handle(
        command,
        _context("expense.reject"),
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.data is expense

    service.get.assert_called_once_with(1)
    service.reject.assert_called_once_with(expense)


def test_return_handler_delegates_to_service():
    """
    ReturnExpenseHandler loads the Expense and delegates
    return processing to ExpenseService.
    """

    expense = _expense("SUBMITTED")
    service = Mock()
    service.get.return_value = expense
    service.return_expense.return_value = expense

    handler = ReturnExpenseHandler(
        service=service
    )

    command = ReturnExpenseCommand(1)

    result = handler.handle(
        command,
        _context("expense.return"),
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.data is expense

    service.get.assert_called_once_with(1)
    service.return_expense.assert_called_once_with(expense)


def test_resubmit_handler_delegates_to_service():
    """
    ResubmitExpenseHandler loads the Expense and delegates
    resubmission to ExpenseService.
    """

    expense = _expense("RETURNED")
    service = Mock()
    service.get.return_value = expense
    service.resubmit.return_value = expense

    handler = ResubmitExpenseHandler(
        service=service
    )

    command = ResubmitExpenseCommand(1)

    result = handler.handle(
        command,
        _context("expense.resubmit"),
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.data is expense

    service.get.assert_called_once_with(1)
    service.resubmit.assert_called_once_with(expense)


def test_close_handler_delegates_to_service():
    """
    CloseExpenseHandler loads the Expense and delegates
    closure to ExpenseService.
    """

    expense = _expense("APPROVED")
    service = Mock()
    service.get.return_value = expense
    service.close.return_value = expense

    handler = CloseExpenseHandler(
        service=service
    )

    command = CloseExpenseCommand(1)

    result = handler.handle(
        command,
        _context("expense.close"),
    )

    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.data is expense

    service.get.assert_called_once_with(1)
    service.close.assert_called_once_with(expense)


def test_submit_handler_returns_invalid_state_failure():
    """
    SubmitExpenseHandler converts a workflow ValueError into
    an ExecutionResult failure.
    """

    expense = _expense("SUBMITTED")
    service = Mock()
    service.get.return_value = expense
    service.submit.side_effect = ValueError(
        "Invalid workflow transition: SUBMITTED -> SUBMITTED"
    )

    handler = SubmitExpenseHandler(
        service=service
    )

    result = handler.handle(
        SubmitExpenseCommand(1),
        _context("expense.submit"),
    )

    assert result.success is False
    assert result.error_code == "INVALID_EXPENSE_STATE"
    assert result.data is expense
    assert (
        result.message
        == "Expense must be in DRAFT status before submission."
    )

    service.get.assert_called_once_with(1)
    service.submit.assert_called_once_with(expense)


def test_approve_handler_returns_invalid_state_failure():
    """
    ApproveExpenseHandler converts a workflow ValueError into
    an ExecutionResult failure.
    """

    expense = _expense("DRAFT")
    service = Mock()
    service.get.return_value = expense
    service.approve.side_effect = ValueError(
        "Invalid workflow transition: DRAFT -> APPROVED"
    )

    handler = ApproveExpenseHandler(
        service=service
    )

    result = handler.handle(
        ApproveExpenseCommand(1),
        _context("expense.approve"),
    )

    assert result.success is False
    assert result.error_code == "INVALID_EXPENSE_STATE"
    assert result.data is expense
    assert (
        result.message
        == "Expense must be in SUBMITTED status before approval."
    )

    service.get.assert_called_once_with(1)
    service.approve.assert_called_once_with(expense)


def test_reject_handler_returns_invalid_state_failure():
    """
    RejectExpenseHandler converts a workflow ValueError into
    an ExecutionResult failure.
    """

    expense = _expense("DRAFT")
    service = Mock()
    service.get.return_value = expense
    service.reject.side_effect = ValueError(
        "Invalid workflow transition: DRAFT -> REJECTED"
    )

    handler = RejectExpenseHandler(
        service=service
    )

    result = handler.handle(
        RejectExpenseCommand(1),
        _context("expense.reject"),
    )

    assert result.success is False
    assert result.error_code == "INVALID_EXPENSE_STATE"
    assert result.data is expense
    assert (
        result.message
        == "Expense must be in SUBMITTED status before rejection."
    )

    service.get.assert_called_once_with(1)
    service.reject.assert_called_once_with(expense)


def test_return_handler_returns_invalid_state_failure():
    """
    ReturnExpenseHandler converts a workflow ValueError into
    an ExecutionResult failure.
    """

    expense = _expense("DRAFT")
    service = Mock()
    service.get.return_value = expense
    service.return_expense.side_effect = ValueError(
        "Invalid workflow transition: DRAFT -> RETURNED"
    )

    handler = ReturnExpenseHandler(
        service=service
    )

    result = handler.handle(
        ReturnExpenseCommand(1),
        _context("expense.return"),
    )

    assert result.success is False
    assert result.error_code == "INVALID_EXPENSE_STATE"
    assert result.data is expense
    assert (
        result.message
        == "Expense must be in SUBMITTED status before return."
    )

    service.get.assert_called_once_with(1)
    service.return_expense.assert_called_once_with(expense)


def test_resubmit_handler_returns_invalid_state_failure():
    """
    ResubmitExpenseHandler converts a workflow ValueError into
    an ExecutionResult failure.
    """

    expense = _expense("DRAFT")
    service = Mock()
    service.get.return_value = expense
    service.resubmit.side_effect = ValueError(
        "Invalid workflow transition: DRAFT -> SUBMITTED"
    )

    handler = ResubmitExpenseHandler(
        service=service
    )

    result = handler.handle(
        ResubmitExpenseCommand(1),
        _context("expense.resubmit"),
    )

    assert result.success is False
    assert result.error_code == "INVALID_EXPENSE_STATE"
    assert result.data is expense
    assert (
        result.message
        == "Expense must be in RETURNED status before resubmission."
    )

    service.get.assert_called_once_with(1)
    service.resubmit.assert_called_once_with(expense)


def test_close_handler_returns_invalid_state_failure():
    """
    CloseExpenseHandler converts a workflow ValueError into
    an ExecutionResult failure.
    """

    expense = _expense("SUBMITTED")
    service = Mock()
    service.get.return_value = expense
    service.close.side_effect = ValueError(
        "Invalid workflow transition: SUBMITTED -> CLOSED"
    )

    handler = CloseExpenseHandler(
        service=service
    )

    result = handler.handle(
        CloseExpenseCommand(1),
        _context("expense.close"),
    )

    assert result.success is False
    assert result.error_code == "INVALID_EXPENSE_STATE"
    assert result.data is expense
    assert (
        result.message
        == "Expense must be in APPROVED status before closure."
    )

    service.get.assert_called_once_with(1)
    service.close.assert_called_once_with(expense)


def test_handlers_do_not_authorize_directly():
    """
    Expense workflow handlers rely on the enterprise execution
    authorization boundary rather than implementing authorization.
    """

    handlers = (
        SubmitExpenseHandler(service=Mock()),
        ApproveExpenseHandler(service=Mock()),
        RejectExpenseHandler(service=Mock()),
        ReturnExpenseHandler(service=Mock()),
        ResubmitExpenseHandler(service=Mock()),
        CloseExpenseHandler(service=Mock()),
    )

    for handler in handlers:
        assert not hasattr(handler, "authorize")


def test_submit_handler_includes_transition_metadata():
    """
    Successful submission exposes previous and new status metadata.
    """

    expense = _expense("DRAFT")
    expense.status = "SUBMITTED"

    service = Mock()
    service.get.return_value = _expense("DRAFT")
    service.submit.side_effect = (
        lambda entity: setattr(entity, "status", "SUBMITTED")
        or entity
    )

    handler = SubmitExpenseHandler(
        service=service
    )

    result = handler.handle(
        SubmitExpenseCommand(1),
        _context("expense.submit"),
    )

    assert result.success is True
    assert result.metadata["expense_id"] == 1
    assert result.metadata["previous_status"] == "DRAFT"
    assert result.metadata["new_status"] == "SUBMITTED"
    assert result.metadata["operation"] == "expense.submit"


def test_approve_handler_includes_transition_metadata():
    """
    Successful approval exposes previous and new status metadata.
    """

    service = Mock()
    expense = _expense("SUBMITTED")
    service.get.return_value = expense

    def approve(entity):
        entity.status = "APPROVED"
        return entity

    service.approve.side_effect = approve

    handler = ApproveExpenseHandler(
        service=service
    )

    result = handler.handle(
        ApproveExpenseCommand(1),
        _context("expense.approve"),
    )

    assert result.success is True
    assert result.metadata["expense_id"] == 1
    assert result.metadata["previous_status"] == "SUBMITTED"
    assert result.metadata["new_status"] == "APPROVED"
    assert result.metadata["operation"] == "expense.approve"
