"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense workflow commands.
"""

from __future__ import annotations

from app.core.execution.commands.base import (
    BaseCommand,
)
from app.core.execution.commands.metadata import (
    CommandMetadata,
)
from app.core.execution.commands.types import (
    CommandType,
)


class SubmitExpenseCommand(
    BaseCommand,
):
    """
    Command to submit an Expense for operational review.
    """

    command_name = "expense.submit"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Submit Expense",
        module_name="EXPENSE",
        operation="expense.submit",
        version="1.0",
        description=(
            "Submit an Expense for operational review."
        ),
        category="workflow",
    )

    def __init__(
        self,
        expense_id: int,
    ) -> None:
        self.expense_id = expense_id

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.expense_id,
            int,
        ):
            raise ValueError(
                "expense_id must be an integer."
            )

        if self.expense_id <= 0:
            raise ValueError(
                "expense_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class ApproveExpenseCommand(
    BaseCommand,
):
    """
    Command to approve a submitted Expense.
    """

    command_name = "expense.approve"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Approve Expense",
        module_name="EXPENSE",
        operation="expense.approve",
        version="1.0",
        description=(
            "Approve a submitted Expense."
        ),
        category="workflow",
    )

    def __init__(
        self,
        expense_id: int,
    ) -> None:
        self.expense_id = expense_id

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.expense_id,
            int,
        ):
            raise ValueError(
                "expense_id must be an integer."
            )

        if self.expense_id <= 0:
            raise ValueError(
                "expense_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class RejectExpenseCommand(
    BaseCommand,
):
    """
    Command to reject a submitted Expense.
    """

    command_name = "expense.reject"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Reject Expense",
        module_name="EXPENSE",
        operation="expense.reject",
        version="1.0",
        description=(
            "Reject a submitted Expense."
        ),
        category="workflow",
    )

    def __init__(
        self,
        expense_id: int,
    ) -> None:
        self.expense_id = expense_id

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.expense_id,
            int,
        ):
            raise ValueError(
                "expense_id must be an integer."
            )

        if self.expense_id <= 0:
            raise ValueError(
                "expense_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class ReturnExpenseCommand(
    BaseCommand,
):
    """
    Command to return a submitted Expense for correction.
    """

    command_name = "expense.return"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Return Expense",
        module_name="EXPENSE",
        operation="expense.return",
        version="1.0",
        description=(
            "Return a submitted Expense for correction."
        ),
        category="workflow",
    )

    def __init__(
        self,
        expense_id: int,
    ) -> None:
        self.expense_id = expense_id

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.expense_id,
            int,
        ):
            raise ValueError(
                "expense_id must be an integer."
            )

        if self.expense_id <= 0:
            raise ValueError(
                "expense_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class ResubmitExpenseCommand(
    BaseCommand,
):
    """
    Command to resubmit a returned Expense for review.
    """

    command_name = "expense.resubmit"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Resubmit Expense",
        module_name="EXPENSE",
        operation="expense.resubmit",
        version="1.0",
        description=(
            "Resubmit a returned Expense for operational review."
        ),
        category="workflow",
    )

    def __init__(
        self,
        expense_id: int,
    ) -> None:
        self.expense_id = expense_id

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.expense_id,
            int,
        ):
            raise ValueError(
                "expense_id must be an integer."
            )

        if self.expense_id <= 0:
            raise ValueError(
                "expense_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


class CloseExpenseCommand(
    BaseCommand,
):
    """
    Command to close an approved Expense.
    """

    command_name = "expense.close"

    command_type = CommandType.EXECUTE

    metadata = CommandMetadata(
        name="Close Expense",
        module_name="EXPENSE",
        operation="expense.close",
        version="1.0",
        description=(
            "Close an approved Expense."
        ),
        category="workflow",
    )

    def __init__(
        self,
        expense_id: int,
    ) -> None:
        self.expense_id = expense_id

    def validate(self) -> None:
        """Validate the command payload."""

        super().validate()

        if not isinstance(
            self.expense_id,
            int,
        ):
            raise ValueError(
                "expense_id must be an integer."
            )

        if self.expense_id <= 0:
            raise ValueError(
                "expense_id must be greater than zero."
            )

    def execute_name(self) -> str:
        """Return the represented operation name."""

        return self.command_name


__all__ = [
    "SubmitExpenseCommand",
    "ApproveExpenseCommand",
    "RejectExpenseCommand",
    "ReturnExpenseCommand",
    "ResubmitExpenseCommand",
    "CloseExpenseCommand",
]
