"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order management form.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional


class PurchaseOrderForm(FlaskForm):
    """
    Form for creating and editing Procurement purchase
    orders.

    Workflow lifecycle transitions are intentionally
    outside this form and belong to the dedicated
    Procurement Workflow stage.
    """

    reference = StringField(
        "Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    supplier_id = SelectField(
        "Supplier",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    order_date = DateField(
        "Order Date",
        validators=[
            DataRequired(),
        ],
    )

    expected_delivery_date = DateField(
        "Expected Delivery Date",
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

    purchase_request_id = SelectField(
        "Purchase Request",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )


__all__ = [
    "PurchaseOrderForm",
]
