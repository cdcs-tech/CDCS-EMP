"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Request management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange


class CateringRequestForm(FlaskForm):
    """
    Form for creating and editing Catering Requests.

    Request lifecycle status is intentionally excluded. Submission
    and cancellation are controlled by the Catering Request service
    and workflow.
    """

    customer_id = SelectField(
        "Customer",
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

    requested_service = StringField(
        "Requested Service",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    service_date = DateField(
        "Service Date",
        validators=[
            DataRequired(),
        ],
    )

    attendance = IntegerField(
        "Attendance",
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
    )

    requirements = TextAreaField(
        "Requirements",
        validators=[
            Length(max=1000),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Length(max=1000),
        ],
    )


__all__ = [
    "CateringRequestForm",
]
