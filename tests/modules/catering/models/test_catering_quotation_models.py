"""
Catering quotation model tests.
"""

from datetime import date
from decimal import Decimal

from app.modules.catering.models import (
    CateringEvent,
    CateringQuotation,
    CateringQuotationLine,
    CateringRequest,
    Customer,
)


def test_catering_quotation_model_metadata():
    assert CateringQuotation.__tablename__ == "catering_quotations"

    assert CateringQuotation.customer_id.property.columns[0].nullable is False
    assert CateringQuotation.event_id.property.columns[0].nullable is False
    assert CateringQuotation.quotation_date.property.columns[0].nullable is False
    assert CateringQuotation.valid_until.property.columns[0].nullable is False
    assert CateringQuotation.status.property.columns[0].nullable is False


def test_catering_quotation_monetary_columns():
    assert str(
        CateringQuotation.adjustment_amount.property.columns[0].type
    ) == "NUMERIC(18, 2)"

    assert str(
        CateringQuotation.subtotal.property.columns[0].type
    ) == "NUMERIC(18, 2)"

    assert str(
        CateringQuotation.total_amount.property.columns[0].type
    ) == "NUMERIC(18, 2)"


def test_catering_quotation_status_default():
    column = CateringQuotation.status.property.columns[0]

    assert column.default is not None
    assert column.default.arg == "DRAFT"


def test_catering_quotation_relationships():
    assert CateringQuotation.customer.property.mapper.class_ is Customer
    assert CateringQuotation.event.property.mapper.class_ is CateringEvent
    assert (
        CateringQuotation.lines.property.mapper.class_
        is CateringQuotationLine
    )


def test_customer_and_event_expose_quotation_relationships():
    assert Customer.quotations.property.mapper.class_ is CateringQuotation
    assert CateringEvent.quotations.property.mapper.class_ is CateringQuotation


def test_catering_quotation_line_model_metadata():
    assert CateringQuotationLine.__tablename__ == "catering_quotation_lines"

    assert (
        CateringQuotationLine.quotation_id.property.columns[0].nullable
        is False
    )
    assert (
        CateringQuotationLine.description.property.columns[0].nullable
        is False
    )
    assert (
        CateringQuotationLine.quantity.property.columns[0].nullable
        is False
    )
    assert (
        CateringQuotationLine.unit.property.columns[0].nullable
        is False
    )
    assert (
        CateringQuotationLine.unit_price.property.columns[0].nullable
        is False
    )
    assert (
        CateringQuotationLine.total_amount.property.columns[0].nullable
        is False
    )


def test_catering_quotation_line_numeric_convention():
    assert str(
        CateringQuotationLine.quantity.property.columns[0].type
    ) == "NUMERIC(18, 3)"

    assert str(
        CateringQuotationLine.unit_price.property.columns[0].type
    ) == "NUMERIC(18, 2)"

    assert str(
        CateringQuotationLine.total_amount.property.columns[0].type
    ) == "NUMERIC(18, 2)"


def test_catering_quotation_line_relationship():
    assert (
        CateringQuotationLine.quotation.property.mapper.class_
        is CateringQuotation
    )
