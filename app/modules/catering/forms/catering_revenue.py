"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Revenue forms.
"""

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
)


class CateringRevenueForm(FlaskForm):
    revenue_reference = StringField(
        "Revenue Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    source_type = SelectField(
        "Source Type",
        choices=[
            ("CATERING_QUOTATION", "Accepted Catering Quotation"),
        ],
        validators=[DataRequired()],
    )

    source_reference = SelectField(
        "Source Reference",
        validators=[DataRequired()],
    )

    customer_id = SelectField(
        "Customer",
        coerce=int,
        validators=[DataRequired()],
    )

    event_id = SelectField(
        "Catering Event",
        coerce=int,
        validators=[DataRequired()],
    )

    amount = DecimalField(
        "Amount",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0),
        ],
    )

    currency = StringField(
        "Currency",
        validators=[
            DataRequired(),
            Length(min=3, max=3),
        ],
    )

    revenue_date = DateField(
        "Revenue Date",
        validators=[DataRequired()],
    )

    revenue_classification = StringField(
        "Revenue Classification",
        validators=[
            Optional(),
            Length(max=100),
        ],
    )


class CateringRevenueEligibilityForm(FlaskForm):
    """Evidence required to establish Catering Revenue eligibility."""

    delivery_evidence = TextAreaField(
        "Delivery Evidence",
        description=(
            "Describe the catering service actually delivered, "
            "including relevant completion evidence."
        ),
        validators=[
            DataRequired(),
            Length(max=2000),
        ],
    )

    eligibility_reason = TextAreaField(
        "Eligibility Reason",
        description=(
            "Explain why the delivered service supports this "
            "revenue amount and revenue date."
        ),
        validators=[
            DataRequired(),
            Length(max=2000),
        ],
    )

    amount_adjustment_reason = TextAreaField(
        "Amount Adjustment Reason",
        description=(
            "If the revenue amount differs from the accepted "
            "quotation total, explain and document the adjustment."
        ),
        validators=[
            Optional(),
            Length(max=2000),
        ],
    )
