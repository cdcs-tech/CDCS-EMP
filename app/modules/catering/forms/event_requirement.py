"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Event requirement management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange


FULFILMENT_TYPE_CHOICES = [
    ("INVENTORY", "Inventory"),
    ("PROCUREMENT", "Procurement"),
]


class EventRequirementForm(FlaskForm):
    """
    Form for creating and editing Catering Event Requirements.

    Event association and lifecycle status are intentionally excluded.
    The parent Event is supplied by the browser route, while lifecycle
    transitions remain the responsibility of EventRequirementService
    and EventRequirementWorkflow.

    Procurement handoff and Inventory fulfilment are intentionally
    outside this form.
    """

    description = StringField(
        "Description",
        validators=[
            DataRequired(),
            Length(max=500),
        ],
    )

    item_reference = StringField(
        "Item Reference",
        validators=[
            Length(max=100),
        ],
    )

    stock_item_id = SelectField(
        "Inventory Stock Item",
        choices=[],
        coerce=int,
        validators=[],
    )

    quantity = DecimalField(
        "Quantity",
        places=3,
        validators=[
            DataRequired(),
            NumberRange(min=0.001),
        ],
    )

    unit = StringField(
        "Unit",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    fulfilment_type = SelectField(
        "Fulfilment Type",
        choices=FULFILMENT_TYPE_CHOICES,
        validators=[
            DataRequired(),
        ],
    )

    required_by_date = DateField(
        "Required By Date",
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Length(max=1000),
        ],
    )


__all__ = [
    "FULFILMENT_TYPE_CHOICES",
    "EventRequirementForm",
]
