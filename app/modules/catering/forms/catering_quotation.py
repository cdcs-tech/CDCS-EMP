"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Quotation management form.
"""

from __future__ import annotations

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import DecimalField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional


class CateringQuotationForm(FlaskForm):
    """
    Form for creating and editing a Catering Quotation.

    Customer and Event relationships are established by the
    application route from the selected Catering Event.

    Quotation status, line totals, subtotal, and total amount
    are deliberately excluded because those values are owned
    by the quotation service and workflow.
    """

    quotation_date = DateField(
        "Quotation Date",
        validators=[
            DataRequired(),
        ],
        default=date.today,
    )

    valid_until = DateField(
        "Valid Until",
        validators=[
            DataRequired(),
        ],
    )

    adjustment_amount = DecimalField(
        "Adjustment Amount",
        validators=[Optional()],
        places=2,
        rounding=None,
        default=0,
    )

    customer_notes = TextAreaField(
        "Customer Notes",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )


class CateringQuotationLineForm(FlaskForm):
    """
    Form fields representing one Catering Quotation line.

    Line totals are calculated by CateringQuotationService and
    are therefore not submitted by the browser.
    """

    description = StringField(
        "Description",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    item_reference = StringField(
        "Item Reference",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )

    quantity = DecimalField(
        "Quantity",
        validators=[
            Optional(),
            NumberRange(min=0.001),
        ],
        places=3,
        rounding=None,
    )

    unit = StringField(
        "Unit",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    unit_price = DecimalField(
        "Unit Price",
        validators=[
            Optional(),
            NumberRange(min=0),
        ],
        places=2,
        rounding=None,
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )


__all__ = [
    "CateringQuotationForm",
    "CateringQuotationLineForm",
]
