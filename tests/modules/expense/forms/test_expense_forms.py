"""
Tests for Expense Management forms.
"""

from datetime import date
from decimal import Decimal

from werkzeug.datastructures import MultiDict

from app.modules.expense.forms import (
    ExpenseClassificationForm,
    ExpenseForm,
)


CLASSIFICATION_CHOICES = [
    (1, "Utilities"),
    (2, "Office Supplies"),
]


def test_expense_classification_form_has_expected_fields(app):
    with app.test_request_context():
        form = ExpenseClassificationForm()

        assert set(form._fields) == {
            "name",
            "code",
            "description",
        }


def test_expense_classification_form_accepts_valid_values(app):
    with app.test_request_context():
        form = ExpenseClassificationForm(
            formdata=MultiDict(
                {
                    "name": "Utilities",
                    "code": "UTIL",
                    "description": "Operational utility expenses",
                }
            )
        )

        assert form.validate() is True
        assert form.name.data == "Utilities"
        assert form.code.data == "UTIL"
        assert form.description.data == "Operational utility expenses"


def test_expense_classification_form_requires_name(app):
    with app.test_request_context():
        form = ExpenseClassificationForm(
            formdata=MultiDict(
                {
                    "name": "",
                    "code": "UTIL",
                    "description": "Operational utility expenses",
                }
            )
        )

        assert form.validate() is False
        assert form.name.errors


def test_expense_classification_form_requires_code(app):
    with app.test_request_context():
        form = ExpenseClassificationForm(
            formdata=MultiDict(
                {
                    "name": "Utilities",
                    "code": "",
                    "description": "Operational utility expenses",
                }
            )
        )

        assert form.validate() is False
        assert form.code.errors


def test_expense_form_has_expected_fields(app):
    with app.test_request_context():
        form = ExpenseForm()

        assert set(form._fields) == {
            "classification_id",
            "description",
            "amount",
            "expense_date",
        }


def test_expense_form_accepts_valid_values(app):
    with app.test_request_context():
        form = ExpenseForm(
            formdata=MultiDict(
                {
                    "classification_id": "1",
                    "description": "Office electricity expense",
                    "amount": "150.00",
                    "expense_date": "2026-09-22",
                }
            )
        )
        form.classification_id.choices = CLASSIFICATION_CHOICES

        assert form.validate() is True
        assert form.classification_id.data == 1
        assert form.description.data == "Office electricity expense"
        assert form.amount.data == Decimal("150.00")
        assert form.expense_date.data == date(2026, 9, 22)


def test_expense_form_requires_classification(app):
    with app.test_request_context():
        form = ExpenseForm(
            formdata=MultiDict(
                {
                    "classification_id": "",
                    "description": "Office electricity expense",
                    "amount": "150.00",
                    "expense_date": "2026-09-22",
                }
            )
        )
        form.classification_id.choices = CLASSIFICATION_CHOICES

        assert form.validate() is False
        assert form.classification_id.errors


def test_expense_form_requires_description(app):
    with app.test_request_context():
        form = ExpenseForm(
            formdata=MultiDict(
                {
                    "classification_id": "1",
                    "description": "",
                    "amount": "150.00",
                    "expense_date": "2026-09-22",
                }
            )
        )
        form.classification_id.choices = CLASSIFICATION_CHOICES

        assert form.validate() is False
        assert form.description.errors


def test_expense_form_requires_amount(app):
    with app.test_request_context():
        form = ExpenseForm(
            formdata=MultiDict(
                {
                    "classification_id": "1",
                    "description": "Office electricity expense",
                    "amount": "",
                    "expense_date": "2026-09-22",
                }
            )
        )
        form.classification_id.choices = CLASSIFICATION_CHOICES

        assert form.validate() is False
        assert form.amount.errors


def test_expense_form_requires_expense_date(app):
    with app.test_request_context():
        form = ExpenseForm(
            formdata=MultiDict(
                {
                    "classification_id": "1",
                    "description": "Office electricity expense",
                    "amount": "150.00",
                    "expense_date": "",
                }
            )
        )
        form.classification_id.choices = CLASSIFICATION_CHOICES

        assert form.validate() is False
        assert form.expense_date.errors
