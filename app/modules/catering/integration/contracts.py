"""
Catering integration contracts.

This module contains explicit, immutable contracts for communication
between Catering and other enterprise capabilities.

The C4 contract describes an approved Expense business fact only.
Catering remains responsible for its own association, consumption,
costing, and later profitability semantics.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


# ---------------------------------------------------------------------------
# C4 Expense integration contract identities
# ---------------------------------------------------------------------------

CATERING_INTEGRATION_PROVIDER = "catering"
CATERING_CONSUME_APPROVED_EXPENSE_OPERATION = "consume_approved_expense"


# ---------------------------------------------------------------------------
# C4 approved Expense integration payload
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ApprovedExpenseCostContribution:
    """
    Expense-owned approved business fact communicated to Catering.

    This contract intentionally contains only facts about the approved
    Expense and its explicit Catering association.

    Catering remains responsible for determining how the approved Expense
    participates in its own costing model. This contract does not contain
    accounting instructions, costing formulas, allocation rules,
    profitability calculations, payment information, or ledger semantics.
    """

    expense_id: int
    description: str
    amount: Decimal
    expense_date: date
    classification_reference: str
    catering_context_type: str
    catering_context_reference: str
    approved_at: datetime
    contribution_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.expense_id, int):
            raise TypeError("expense_id must be an integer.")

        if self.expense_id <= 0:
            raise ValueError("expense_id must be greater than zero.")

        required_strings = (
            self.description,
            self.classification_reference,
            self.catering_context_type,
            self.catering_context_reference,
            self.contribution_id,
        )

        if any(
            not isinstance(value, str) or not value.strip()
            for value in required_strings
        ):
            raise ValueError(
                "Approved Expense required string fields "
                "must be non-empty."
            )

        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be a Decimal.")

        if self.amount < Decimal("0"):
            raise ValueError("amount must not be negative.")

        if not isinstance(self.expense_date, date):
            raise TypeError("expense_date must be a date.")

        if not isinstance(self.approved_at, datetime):
            raise TypeError("approved_at must be a datetime.")

        if not isinstance(self.contribution_id, str):
            raise TypeError("contribution_id must be a string.")


__all__ = [
    "CATERING_INTEGRATION_PROVIDER",
    "CATERING_CONSUME_APPROVED_EXPENSE_OPERATION",
    "ApprovedExpenseCostContribution",
]
