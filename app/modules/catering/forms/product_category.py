"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product category management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class ProductCategoryForm(FlaskForm):
    """
    Form for creating and editing Catering product categories.
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
    "ProductCategoryForm",
]
