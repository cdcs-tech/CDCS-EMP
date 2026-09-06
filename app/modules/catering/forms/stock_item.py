"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock item management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import DecimalField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import ValidationError


def _non_negative(form, field):
    """
    Ensure an optional numeric threshold is not negative.
    """
    if field.data is not None and field.data < 0:
        raise ValidationError(
            "Value must be greater than or equal to 0."
        )


class StockItemForm(FlaskForm):
    """
    Form for creating and editing Catering stock items.
    """

    product_id = SelectField(
        "Product",
        coerce=int,
        choices=[],
        validators=[DataRequired()],
    )

    minimum_level = DecimalField(
        "Minimum Level",
        places=3,
        validators=[Optional(), _non_negative],
    )

    reorder_level = DecimalField(
        "Reorder Level",
        places=3,
        validators=[Optional(), _non_negative],
    )

    is_active = BooleanField(
        "Active",
        default=True,
    )


__all__ = ["StockItemForm"]
