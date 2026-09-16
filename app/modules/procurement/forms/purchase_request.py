"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase request management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional


class PurchaseRequestForm(FlaskForm):
    """
    Form for creating and editing Procurement purchase
    requests.

    Workflow lifecycle transitions are intentionally outside
    this form and belong to the dedicated Procurement Workflow
    stage.
    """

    reference = StringField(
        "Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    purchase_requirement_id = SelectField(
        "Purchase Requirement",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    request_date = DateField(
        "Request Date",
        validators=[
            DataRequired(),
        ],
    )

    required_by_date = DateField(
        "Required By Date",
        validators=[
            Optional(),
        ],
    )

    status = StringField(
        "Status",
        validators=[
            DataRequired(),
            Length(max=20),
        ],
    )

    justification = StringField(
        "Justification",
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
    "PurchaseRequestForm",
]
