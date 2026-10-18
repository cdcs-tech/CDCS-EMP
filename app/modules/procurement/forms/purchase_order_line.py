
"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase order line forms.
"""

from __future__ import annotations

from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class PurchaseOrderLineForm(FlaskForm):
    """
    Form for creating and editing Purchase Order Lines.
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

    stock_item_reference = SelectField(
        "Inventory Product",
        choices=[("", "Not inventory-managed")],
        coerce=str,
        default="",
        validators=[
            Length(max=100),
        ],
    )

    quantity = DecimalField(
        "Quantity",
        places=3,
        validators=[
            DataRequired(),
            NumberRange(
                min=Decimal("0.001"),
                message="Quantity must be greater than zero.",
            ),
        ],
    )

    unit = StringField(
        "Unit",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    unit_price = DecimalField(
        "Unit Price",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(
                min=Decimal("0.00"),
                message="Unit price cannot be negative.",
            ),
        ],
    )

    total_amount = DecimalField(
        "Total Amount",
        places=2,
        validators=[
            DataRequired(),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Length(max=1000),
        ],
    )


__all__ = [
    "PurchaseOrderLineForm",
]
