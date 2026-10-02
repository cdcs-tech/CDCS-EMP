"""
Catering integration contract tests.
"""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.modules.catering.integration import (
    ApprovedExpenseCostContribution,
    CateringRevenueContribution,
    CATERING_CONSUME_APPROVED_EXPENSE_OPERATION,
    CATERING_INTEGRATION_PROVIDER,
)


def build_expense_contribution(**overrides):
    values = {
        "expense_id": 901,
        "description": "Catering venue decoration",
        "amount": Decimal("450.00"),
        "expense_date": date(2026, 9, 30),
        "classification_reference": "CATERING_DECORATION",
        "catering_context_type": "CATERING_EVENT",
        "catering_context_reference": "EVENT-2026-001",
        "approved_at": datetime(
            2026,
            9,
            30,
            14,
            30,
            tzinfo=timezone.utc,
        ),
        "contribution_id": (
            "expense:901:catering:event:EVENT-2026-001"
        ),
    }
    values.update(overrides)
    return ApprovedExpenseCostContribution(**values)


def build_revenue_contribution(**overrides):
    values = {
        "revenue_reference": "REV-2026-0001",
        "source_type": "CATERING_REVENUE",
        "source_reference": "EVENT-2026-001",
        "amount": Decimal("2500.00"),
        "currency": "USD",
        "revenue_date": date(2026, 9, 30),
        "revenue_classification": "CATERING_SERVICE",
        "contribution_id": "catering-revenue:REV-2026-0001",
    }
    values.update(overrides)
    return CateringRevenueContribution(**values)


# ---------------------------------------------------------------------------
# Existing C4 contract tests
# ---------------------------------------------------------------------------


def test_catering_provider_identity():
    assert CATERING_INTEGRATION_PROVIDER == "catering"


def test_catering_consume_approved_expense_operation_identity():
    assert (
        CATERING_CONSUME_APPROVED_EXPENSE_OPERATION
        == "consume_approved_expense"
    )


def test_valid_approved_expense_contract_accepts_expected_fields():
    contribution = build_expense_contribution()

    assert contribution.expense_id == 901
    assert contribution.description == "Catering venue decoration"
    assert contribution.amount == Decimal("450.00")
    assert contribution.expense_date == date(2026, 9, 30)
    assert contribution.classification_reference == "CATERING_DECORATION"
    assert contribution.catering_context_type == "CATERING_EVENT"
    assert contribution.catering_context_reference == "EVENT-2026-001"


def test_approved_expense_contract_is_immutable():
    contribution = build_expense_contribution()

    with pytest.raises(AttributeError):
        contribution.amount = Decimal("500.00")


def test_expense_id_must_be_integer():
    with pytest.raises(TypeError):
        build_expense_contribution(expense_id="901")


def test_expense_id_must_be_positive():
    with pytest.raises(ValueError):
        build_expense_contribution(expense_id=0)


@pytest.mark.parametrize(
    "field",
    [
        "description",
        "classification_reference",
        "catering_context_type",
        "catering_context_reference",
        "contribution_id",
    ],
)
def test_expense_required_strings_reject_empty_values(field):
    with pytest.raises(ValueError):
        build_expense_contribution(**{field: ""})


def test_expense_amount_must_use_decimal():
    with pytest.raises(TypeError):
        build_expense_contribution(amount=450)


def test_expense_amount_must_not_be_negative():
    with pytest.raises(ValueError):
        build_expense_contribution(amount=Decimal("-1"))


def test_expense_date_must_be_date():
    with pytest.raises(TypeError):
        build_expense_contribution(expense_date="2026-09-30")


def test_expense_approved_at_must_be_datetime():
    with pytest.raises(TypeError):
        build_expense_contribution(
            approved_at="2026-09-30T14:30:00Z"
        )


def test_expense_contract_contains_no_accounting_or_costing_semantics():
    contribution = build_expense_contribution()

    assert not hasattr(contribution, "ledger_account")
    assert not hasattr(contribution, "journal_entry")
    assert not hasattr(contribution, "payment_reference")
    assert not hasattr(contribution, "invoice_reference")
    assert not hasattr(contribution, "cost_formula")
    assert not hasattr(contribution, "allocation_rule")
    assert not hasattr(contribution, "profitability")


# ---------------------------------------------------------------------------
# A2.6 Catering Revenue contribution tests
# ---------------------------------------------------------------------------


def test_valid_catering_revenue_contribution_accepts_expected_fields():
    contribution = build_revenue_contribution()

    assert contribution.revenue_reference == "REV-2026-0001"
    assert contribution.source_type == "CATERING_REVENUE"
    assert contribution.source_reference == "EVENT-2026-001"
    assert contribution.amount == Decimal("2500.00")
    assert contribution.currency == "USD"
    assert contribution.revenue_date == date(2026, 9, 30)
    assert contribution.revenue_classification == "CATERING_SERVICE"


def test_catering_revenue_contribution_is_immutable():
    contribution = build_revenue_contribution()

    with pytest.raises(AttributeError):
        contribution.amount = Decimal("3000.00")


@pytest.mark.parametrize(
    "field",
    [
        "revenue_reference",
        "source_type",
        "source_reference",
        "currency",
        "contribution_id",
    ],
)
def test_revenue_required_strings_reject_empty_values(field):
    with pytest.raises(ValueError):
        build_revenue_contribution(**{field: ""})


def test_revenue_amount_must_use_decimal():
    with pytest.raises(TypeError):
        build_revenue_contribution(amount=2500)


def test_revenue_amount_must_not_be_negative():
    with pytest.raises(ValueError):
        build_revenue_contribution(amount=Decimal("-1"))


def test_revenue_currency_must_be_three_letters():
    with pytest.raises(ValueError):
        build_revenue_contribution(currency="US")


def test_revenue_date_must_be_date():
    with pytest.raises(TypeError):
        build_revenue_contribution(
            revenue_date="2026-09-30"
        )


def test_revenue_classification_may_be_omitted():
    contribution = build_revenue_contribution(
        revenue_classification=None
    )

    assert contribution.revenue_classification is None


def test_revenue_classification_rejects_empty_string():
    with pytest.raises(ValueError):
        build_revenue_contribution(
            revenue_classification=""
        )


def test_revenue_contribution_identity_is_distinct_from_revenue_reference():
    contribution = build_revenue_contribution()

    assert contribution.contribution_id != contribution.revenue_reference


def test_revenue_contribution_contains_no_finance_accounting_semantics():
    contribution = build_revenue_contribution()

    assert not hasattr(contribution, "finance_revenue_id")
    assert not hasattr(contribution, "invoice_reference")
    assert not hasattr(contribution, "receipt_reference")
    assert not hasattr(contribution, "payment_reference")
    assert not hasattr(contribution, "ledger_account")
    assert not hasattr(contribution, "journal_entry")
    assert not hasattr(contribution, "accounting_classification")
    assert not hasattr(contribution, "tax_treatment")
