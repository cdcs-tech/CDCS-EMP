"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Purchase Requirement creation form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import DecimalField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional


class CateringPurchaseRequirementForm(FlaskForm):
    """
    Form for creating a Catering-owned Purchase Requirement.

    The parent Event Requirement and lifecycle status are supplied
    or managed by the application service. Procurement handoff is
    handled separately.
    """

    description = StringField(
        "Description",
        validators=[
            DataRequired(),
            Length(max=500),
        ],
    )

    item_reference = StringField(
        "Item Reference",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    quantity = DecimalField(
        "Quantity",
        places=3,
        validators=[
            DataRequired(),
            NumberRange(min=0.001),
        ],
    )

    unit = StringField(
        "Unit",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    required_by_date = DateField(
        "Required By Date",
        validators=[Optional()],
    )

    justification = TextAreaField(
        "Justification",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )


__all__ = [
    "CateringPurchaseRequirementForm",
]
