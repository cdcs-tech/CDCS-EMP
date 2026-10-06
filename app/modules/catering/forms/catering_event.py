"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import IntegerField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange


class CateringEventForm(FlaskForm):
    """
    Form for editing the operational fields of a Catering Event.

    Request and customer relationships are intentionally excluded.
    They are established by the Request -> Event coordination service.
    Event status is also excluded because lifecycle transitions are
    controlled by the Catering Event service and workflow.
    """

    event_date = DateField(
        "Event Date",
        validators=[
            DataRequired(),
        ],
    )

    service_details = TextAreaField(
        "Service Details",
        validators=[
            DataRequired(),
            Length(max=1000),
        ],
    )

    attendance = IntegerField(
        "Attendance",
        validators=[
            DataRequired(),
            NumberRange(min=1),
        ],
    )

    operational_notes = TextAreaField(
        "Operational Notes",
        validators=[
            Length(max=1000),
        ],
    )


__all__ = [
    "CateringEventForm",
]
