"""
Catering integration contracts.

This module contains explicit, immutable contracts for communication
between Catering and other enterprise capabilities.

The C4 contract describes an approved Expense business fact only.
The A2.6 revenue contract describes an already-established Catering
Revenue business fact for later Finance integration.

Catering remains authoritative for its originating business facts.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


# ---------------------------------------------------------------------------
# Enterprise provider identity
# ---------------------------------------------------------------------------

CATERING_INTEGRATION_PROVIDER = "catering"


# ---------------------------------------------------------------------------
# C4 Expense integration contract identity
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# A2.6 Catering Revenue contribution
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CateringRevenueContribution:
    """
    Immutable Catering Revenue business fact prepared for later integration.

    The contribution represents an already-established authoritative
    Catering Revenue fact. It does not perform or infer revenue recognition.

    The contract intentionally contains source-owned business facts only.
    Finance-specific accounting treatment, financial classifications,
    invoices, receipts, payments, ledger entries, and journal instructions
    remain outside this contract.
    """

    revenue_reference: str
    source_type: str
    source_reference: str
    amount: Decimal
    currency: str
    revenue_date: date
    revenue_classification: str | None
    contribution_id: str

    def __post_init__(self) -> None:
        required_strings = (
            self.revenue_reference,
            self.source_type,
            self.source_reference,
            self.currency,
            self.contribution_id,
        )

        if any(
            not isinstance(value, str) or not value.strip()
            for value in required_strings
        ):
            raise ValueError(
                "Catering Revenue required string fields "
                "must be non-empty."
            )

        if not isinstance(self.amount, Decimal):
            raise TypeError("amount must be a Decimal.")

        if self.amount < Decimal("0"):
            raise ValueError("amount must not be negative.")

        if not isinstance(self.currency, str):
            raise TypeError("currency must be a string.")

        if len(self.currency.strip()) != 3:
            raise ValueError(
                "currency must be a three-letter currency code."
            )

        if not isinstance(self.revenue_date, date):
            raise TypeError("revenue_date must be a date.")

        if self.revenue_classification is not None and (
            not isinstance(self.revenue_classification, str)
            or not self.revenue_classification.strip()
        ):
            raise ValueError(
                "revenue_classification must be non-empty when provided."
            )


__all__ = [
    "CATERING_INTEGRATION_PROVIDER",
    "CATERING_CONSUME_APPROVED_EXPENSE_OPERATION",
    "ApprovedExpenseCostContribution",
    "CateringRevenueContribution",
]
