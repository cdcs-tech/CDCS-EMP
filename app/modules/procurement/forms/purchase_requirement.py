"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase requirement management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional


class PurchaseRequirementForm(FlaskForm):
    """
    Form for creating and editing Procurement purchase
    requirements.

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

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(),
            Length(max=500),
        ],
    )

    source_module = StringField(
        "Source Module",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    source_type = StringField(
        "Source Type",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    source_reference = StringField(
        "Source Reference",
        validators=[
            Optional(),
            Length(max=100),
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


__all__ = [
    "PurchaseRequirementForm",
]
