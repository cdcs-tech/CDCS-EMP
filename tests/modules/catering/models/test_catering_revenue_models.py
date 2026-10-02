"""Tests for the Catering revenue domain model."""

from app.modules.catering.models import CateringRevenue


def test_catering_revenue_model_metadata():
    """Verify the core Catering revenue model metadata."""

    assert CateringRevenue.__tablename__ == "catering_revenues"

    assert (
        CateringRevenue.revenue_reference.property.columns[0].nullable
        is False
    )
    assert (
        CateringRevenue.source_type.property.columns[0].nullable
        is False
    )
    assert (
        CateringRevenue.source_reference.property.columns[0].nullable
        is False
    )

    assert (
        CateringRevenue.customer_id.property.columns[0].nullable
        is True
    )
    assert (
        CateringRevenue.event_id.property.columns[0].nullable
        is True
    )


def test_catering_revenue_monetary_columns():
    """Verify the fixed-precision revenue amount."""

    assert (
        str(CateringRevenue.amount.property.columns[0].type)
        == "NUMERIC(18, 2)"
    )


def test_catering_revenue_monetary_and_date_fields():
    """Verify the required financial fact fields."""

    assert (
        CateringRevenue.amount.property.columns[0].nullable
        is False
    )
    assert (
        CateringRevenue.currency.property.columns[0].nullable
        is False
    )
    assert (
        CateringRevenue.revenue_date.property.columns[0].nullable
        is False
    )


def test_catering_revenue_status_default():
    """Verify the initial revenue lifecycle state."""

    column = CateringRevenue.status.property.columns[0]

    assert column.default is not None
    assert column.default.arg == "DRAFT"


def test_catering_revenue_recognition_timestamp_is_optional():
    """Verify recognition timestamp is populated only when recognized."""

    assert (
        CateringRevenue.recognized_at.property.columns[0].nullable
        is True
    )


def test_catering_revenue_identity_is_unique():
    """Verify the stable Catering revenue identity."""

    column = CateringRevenue.revenue_reference.property.columns[0]

    assert column.unique is True
