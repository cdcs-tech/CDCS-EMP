"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense workflow command handlers.
"""

from __future__ import annotations

from app.core.execution.context import (
    ExecutionContext,
)
from app.core.execution.handlers.base import (
    BaseCommandHandler,
)
from app.core.execution.results import (
    ExecutionResult,
)

from app.modules.expense.commands import (
    ApproveExpenseCommand,
    CloseExpenseCommand,
    RejectExpenseCommand,
    ResubmitExpenseCommand,
    ReturnExpenseCommand,
    SubmitExpenseCommand,
)
from app.modules.expense.services import (
    ExpenseService,
)


class SubmitExpenseHandler(BaseCommandHandler):
    """
    Handle Expense submission.
    """

    command_type = SubmitExpenseCommand

    def __init__(
        self,
        service: ExpenseService | None = None,
    ) -> None:
        self.service = (
            service
            or ExpenseService()
        )

    def handle(
        self,
        command: SubmitExpenseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Submit an Expense through its workflow.
        """

        expense = self.service.get(
            command.expense_id
        )

        previous_status = expense.status

        try:
            self.service.submit(
                expense
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Expense must be in "
                    "DRAFT status before submission."
                ),
                error_code=(
                    "INVALID_EXPENSE_STATE"
                ),
                data=expense,
            )

        return ExecutionResult.success_result(
            data=expense,
            message=(
                "Expense submitted successfully."
            ),
            metadata={
                "expense_id": expense.id,
                "previous_status": previous_status,
                "new_status": expense.status,
                "operation": context.operation,
            },
        )


class ApproveExpenseHandler(BaseCommandHandler):
    """
    Handle Expense approval.
    """

    command_type = ApproveExpenseCommand

    def __init__(
        self,
        service: ExpenseService | None = None,
    ) -> None:
        self.service = (
            service
            or ExpenseService()
        )

    def handle(
        self,
        command: ApproveExpenseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Approve an Expense through its workflow.
        """

        expense = self.service.get(
            command.expense_id
        )

        previous_status = expense.status

        try:
            self.service.approve(
                expense
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Expense must be in "
                    "SUBMITTED status before approval."
                ),
                error_code=(
                    "INVALID_EXPENSE_STATE"
                ),
                data=expense,
            )

        return ExecutionResult.success_result(
            data=expense,
            message=(
                "Expense approved successfully."
            ),
            metadata={
                "expense_id": expense.id,
                "previous_status": previous_status,
                "new_status": expense.status,
                "operation": context.operation,
            },
        )


class RejectExpenseHandler(BaseCommandHandler):
    """
    Handle Expense rejection.
    """

    command_type = RejectExpenseCommand

    def __init__(
        self,
        service: ExpenseService | None = None,
    ) -> None:
        self.service = (
            service
            or ExpenseService()
        )

    def handle(
        self,
        command: RejectExpenseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Reject an Expense through its workflow.
        """

        expense = self.service.get(
            command.expense_id
        )

        previous_status = expense.status

        try:
            self.service.reject(
                expense
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Expense must be in "
                    "SUBMITTED status before rejection."
                ),
                error_code=(
                    "INVALID_EXPENSE_STATE"
                ),
                data=expense,
            )

        return ExecutionResult.success_result(
            data=expense,
            message=(
                "Expense rejected successfully."
            ),
            metadata={
                "expense_id": expense.id,
                "previous_status": previous_status,
                "new_status": expense.status,
                "operation": context.operation,
            },
        )


class ReturnExpenseHandler(BaseCommandHandler):
    """
    Handle returning an Expense for correction.
    """

    command_type = ReturnExpenseCommand

    def __init__(
        self,
        service: ExpenseService | None = None,
    ) -> None:
        self.service = (
            service
            or ExpenseService()
        )

    def handle(
        self,
        command: ReturnExpenseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Return an Expense to the RETURNED state
        through its workflow.
        """

        expense = self.service.get(
            command.expense_id
        )

        previous_status = expense.status

        try:
            self.service.return_expense(
                expense
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Expense must be in "
                    "SUBMITTED status before return."
                ),
                error_code=(
                    "INVALID_EXPENSE_STATE"
                ),
                data=expense,
            )

        return ExecutionResult.success_result(
            data=expense,
            message=(
                "Expense returned for correction successfully."
            ),
            metadata={
                "expense_id": expense.id,
                "previous_status": previous_status,
                "new_status": expense.status,
                "operation": context.operation,
            },
        )


class ResubmitExpenseHandler(BaseCommandHandler):
    """
    Handle Expense resubmission.
    """

    command_type = ResubmitExpenseCommand

    def __init__(
        self,
        service: ExpenseService | None = None,
    ) -> None:
        self.service = (
            service
            or ExpenseService()
        )

    def handle(
        self,
        command: ResubmitExpenseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Resubmit an Expense through its workflow.
        """

        expense = self.service.get(
            command.expense_id
        )

        previous_status = expense.status

        try:
            self.service.resubmit(
                expense
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Expense must be in "
                    "RETURNED status before resubmission."
                ),
                error_code=(
                    "INVALID_EXPENSE_STATE"
                ),
                data=expense,
            )

        return ExecutionResult.success_result(
            data=expense,
            message=(
                "Expense resubmitted successfully."
            ),
            metadata={
                "expense_id": expense.id,
                "previous_status": previous_status,
                "new_status": expense.status,
                "operation": context.operation,
            },
        )


class CloseExpenseHandler(BaseCommandHandler):
    """
    Handle Expense closure.
    """

    command_type = CloseExpenseCommand

    def __init__(
        self,
        service: ExpenseService | None = None,
    ) -> None:
        self.service = (
            service
            or ExpenseService()
        )

    def handle(
        self,
        command: CloseExpenseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        Close an approved Expense through its workflow.
        """

        expense = self.service.get(
            command.expense_id
        )

        previous_status = expense.status

        try:
            self.service.close(
                expense
            )
        except ValueError:
            return ExecutionResult.failure_result(
                message=(
                    "Expense must be in "
                    "APPROVED status before closure."
                ),
                error_code=(
                    "INVALID_EXPENSE_STATE"
                ),
                data=expense,
            )

        return ExecutionResult.success_result(
            data=expense,
            message=(
                "Expense closed successfully."
            ),
            metadata={
                "expense_id": expense.id,
                "previous_status": previous_status,
                "new_status": expense.status,
                "operation": context.operation,
            },
        )


__all__ = [
    "ApproveExpenseHandler",
    "CloseExpenseHandler",
    "RejectExpenseHandler",
    "ResubmitExpenseHandler",
    "ReturnExpenseHandler",
    "SubmitExpenseHandler",
]
