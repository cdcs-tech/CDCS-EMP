"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense classification management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class ExpenseClassificationForm(FlaskForm):
    """
    Form for creating and editing Expense Management
    expense classifications.
    """

    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    code = StringField(
        "Code",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Length(max=500),
        ],
    )


__all__ = [
    "ExpenseClassificationForm",
]
