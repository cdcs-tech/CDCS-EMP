"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase request line forms.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class PurchaseRequestLineForm(FlaskForm):
    """
    Form for creating and editing Purchase Request Lines.
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
            Length(max=100),
        ],
    )

    quantity = DecimalField(
        "Quantity",
        places=3,
        validators=[
            DataRequired(),
        ],
    )

    unit = StringField(
        "Unit",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    estimated_unit_cost = DecimalField(
        "Estimated Unit Cost",
        places=2,
        validators=[
            Optional(),
        ],
    )

    estimated_total = DecimalField(
        "Estimated Total",
        places=2,
        validators=[
            Optional(),
        ],
    )

    required_by_date = DateField(
        "Required By Date",
        validators=[
            Optional(),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Length(max=1000),
        ],
    )
