
"""
Catering Expense Cost Association form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange


class CateringExpenseCostAssociationForm(FlaskForm):
    """Form for associating an existing Expense with a Catering Event."""

    expense_id = IntegerField(
        "Expense ID",
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
    )

    event_id = IntegerField(
        "Catering Event ID",
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
    )


__all__ = [
    "CateringExpenseCostAssociationForm",
]
