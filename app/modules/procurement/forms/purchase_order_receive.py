from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import NumberRange
from wtforms.validators import Optional


class PurchaseOrderReceiveForm(FlaskForm):
    """
    Browser form for submitting a Purchase Order receipt
    to Inventory through the Procurement execution boundary.
    """

    purchase_order_line_id = SelectField(
        "Purchase Order Line",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    inventory_location_reference = StringField(
        "Inventory Location Code",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    quantity_received = DecimalField(
        "Quantity Received",
        places=3,
        validators=[
            DataRequired(),
            NumberRange(min=0.001),
        ],
    )

    received_at = StringField(
        "Received At",
        validators=[
            DataRequired(),
            Length(max=30),
        ],
    )

    receiving_reference = StringField(
        "Receiving Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional(),
            Length(max=1000),
        ],
    )


__all__ = [
    "PurchaseOrderReceiveForm",
]
