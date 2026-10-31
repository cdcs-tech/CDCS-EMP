"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional


class ExpenseForm(FlaskForm):
    """
    Form for creating and editing Expense Management
    operational expense records.
    """

    classification_id = SelectField(
        "Expense Classification",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    description = StringField(
        "Description",
        validators=[
            DataRequired(),
            Length(max=500),
        ],
    )

    amount = DecimalField(
        "Amount",
        places=2,
        validators=[
            DataRequired(),
        ],
    )

    currency = SelectField(
        "Currency",
        choices=[
            ("USD", "USD — US Dollar"),
            ("SSP", "SSP — South Sudanese Pound"),
            ("", "Unknown — not yet verified"),
        ],
        default="USD",
        validators=[
            Optional(),
        ],
    )

    expense_date = DateField(
        "Expense Date",
        validators=[
            DataRequired(),
        ],
    )


__all__ = [
    "ExpenseForm",
]
