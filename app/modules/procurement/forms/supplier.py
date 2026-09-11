"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Supplier management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class SupplierForm(FlaskForm):
    """
    Form for creating and editing Procurement suppliers.
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

    supplier_type = StringField(
        "Supplier Type",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    contact_information = TextAreaField(
        "Contact Information",
        validators=[
            Length(max=500),
        ],
    )

    address_information = TextAreaField(
        "Address Information",
        validators=[
            Length(max=500),
        ],
    )

    status = StringField(
        "Status",
        validators=[
            DataRequired(),
            Length(max=20),
        ],
    )


__all__ = [
    "SupplierForm",
]
