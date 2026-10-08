"""
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
)


class CateringRevenueForm(FlaskForm):
    """
    Form for creating and editing a Catering Revenue business record.

    Revenue lifecycle state and recognition timestamp are intentionally
    excluded because they are controlled by the Catering Revenue service
    and workflow.
    """

    revenue_reference = StringField(
        "Revenue Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    source_type = StringField(
        "Source Type",
        validators=[
            DataRequired(),
            Length(max=50),
        ],
    )

    source_reference = StringField(
        "Source Reference",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    customer_id = SelectField(
        "Customer",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
    )

    event_id = SelectField(
        "Catering Event",
        coerce=int,
        choices=[],
        validators=[
            DataRequired(),
        ],
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
        validators=[
            DataRequired(),
        ],
    )

    revenue_classification = StringField(
        "Revenue Classification",
        validators=[
            Length(max=100),
        ],
    )
