"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock movement management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError


MOVEMENT_TYPE_CHOICES = [
    ("OPENING_BALANCE", "Opening Balance"),
    ("RECEIPT", "Receipt"),
    ("ISSUE", "Issue"),
    ("ADJUSTMENT", "Adjustment"),
    ("TRANSFER", "Transfer"),
]


def _non_zero(form, field):
    """
    Ensure the movement quantity is not zero.
    """

    if field.data is not None and field.data == 0:
        raise ValidationError(
            "Quantity must not be zero."
        )


class StockMovementForm(FlaskForm):
    """
    Form for creating and editing Catering stock movements.

    Posting, balance updates, authorization, and immutable
    lifecycle transitions remain the responsibility of the
    StockMovementService.
    """

    stock_item_id = SelectField(
        "Stock Item",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    location_id = SelectField(
        "Location",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    movement_type = SelectField(
        "Movement Type",
        choices=MOVEMENT_TYPE_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    quantity = DecimalField(
        "Quantity",
        places=3,
        validators=[
            DataRequired(),
            _non_zero,
        ],
    )

    reference = StringField(
        "Reference",
        validators=[
            Length(max=100),
        ],
    )

    reason = TextAreaField(
        "Reason",
        validators=[
            Length(max=500),
        ],
    )

    occurred_at = DateTimeLocalField(
        "Occurred At",
        validators=[
            DataRequired(),
        ],
        format="%Y-%m-%dT%H:%M",
    )


__all__ = [
    "MOVEMENT_TYPE_CHOICES",
    "StockMovementForm",
]
