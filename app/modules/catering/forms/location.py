"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory location management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class InventoryLocationForm(FlaskForm):
    """
    Form for creating and editing Catering inventory locations.
    """

    code = StringField(
        "Code",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Length(max=500),
        ],
    )

    is_active = BooleanField(
        "Active",
        default=True,
    )


__all__ = ["InventoryLocationForm"]
