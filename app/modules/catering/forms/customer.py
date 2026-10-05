"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Customer management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length


class CustomerForm(FlaskForm):
    """
    Form for creating and editing Catering customers.
    """

    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    customer_type = SelectField(
        "Customer Type",
        choices=[
            ("INDIVIDUAL", "Individual"),
            ("ORGANIZATION", "Organization"),
        ],
        validators=[
            DataRequired(),
        ],
    )

    phone = StringField(
        "Phone",
        validators=[
            Length(max=50),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            Email(),
            Length(max=150),
        ],
    )

    address = TextAreaField(
        "Address",
        validators=[
            Length(max=500),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Length(max=1000),
        ],
    )


__all__ = [
    "CustomerForm",
]
