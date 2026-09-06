"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock transfer management form.
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


def _positive_quantity(form, field):
    """
    Ensure the transfer quantity is greater than zero.
    """
    if field.data is not None and field.data <= 0:
        raise ValidationError(
            "Quantity must be greater than zero."
        )


class StockTransferForm(FlaskForm):
    """
    Form for creating and editing Catering stock transfers.

    Source availability, location distinctness, authorization,
    posting, balance updates, movement creation, and transaction
    handling remain the responsibility of StockTransferService.
    """

    stock_item_id = SelectField(
        "Stock Item",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    source_location_id = SelectField(
        "Source Location",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    destination_location_id = SelectField(
        "Destination Location",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    quantity = DecimalField(
        "Quantity",
        places=3,
        validators=[
            DataRequired(),
            _positive_quantity,
        ],
    )

    reference = StringField(
        "Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    reason = TextAreaField(
        "Reason",
        validators=[
            DataRequired(),
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
    "StockTransferForm",
]
