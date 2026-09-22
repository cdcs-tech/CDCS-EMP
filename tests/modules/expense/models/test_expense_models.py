"""
Focused tests for the Expense Management domain models.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import inspect

from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)


def test_expense_classification_has_expected_table_and_columns():
    """
    ExpenseClassification exposes the approved Expense Foundation
    master-data structure.
    """

    mapper = inspect(ExpenseClassification)

    assert mapper.local_table.name == "expense_classifications"

    assert {
        "name",
        "code",
        "description",
        "is_active",
    }.issubset(
        {column.key for column in mapper.columns}
    )


def test_expense_has_expected_table_and_columns():
    """
    Expense exposes only the approved initial operational fields.
    """

    mapper = inspect(Expense)

    assert mapper.local_table.name == "expenses"

    assert {
        "classification_id",
        "description",
        "amount",
        "expense_date",
    }.issubset(
        {column.key for column in mapper.columns}
    )


def test_expense_classification_has_one_to_many_relationship():
    """
    ExpenseClassification owns the one-to-many relationship to Expense.
    """

    relationship = inspect(
        ExpenseClassification
    ).relationships["expenses"]

    assert relationship.mapper.class_ is Expense
    assert relationship.uselist is True
    assert relationship.back_populates == "classification"


def test_expense_has_classification_relationship():
    """
    Expense references its ExpenseClassification through the internal
    Expense Management relationship.
    """

    relationship = inspect(
        Expense
    ).relationships["classification"]

    assert relationship.mapper.class_ is ExpenseClassification
    assert relationship.uselist is False
    assert relationship.back_populates == "expenses"


def test_expense_classification_can_be_constructed():
    """
    ExpenseClassification can be constructed using the approved
    master-data fields.
    """

    classification = ExpenseClassification(
        name="Utilities",
        code="UTIL",
        description="Operational utility expenses",
        is_active=True,
    )

    assert classification.name == "Utilities"
    assert classification.code == "UTIL"
    assert classification.description == "Operational utility expenses"
    assert classification.is_active is True


def test_expense_can_be_constructed():
    """
    Expense can be constructed using the approved operational fields.
    """

    expense = Expense(
        classification_id=1,
        description="Office electricity expense",
        amount=Decimal("150.00"),
        expense_date=date(2026, 9, 22),
    )

    assert expense.classification_id == 1
    assert expense.description == "Office electricity expense"
    assert expense.amount == Decimal("150.00")
    assert expense.expense_date == date(2026, 9, 22)
