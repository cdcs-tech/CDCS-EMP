"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class ProductForm(FlaskForm):
    """
    Form for creating and editing Catering products.
    """

    category_id = SelectField(
        "Category",
        coerce=int,
        validators=[
            DataRequired(),
        ],
    )

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

    unit = StringField(
        "Unit",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )


__all__ = [
    "ProductForm",
]
