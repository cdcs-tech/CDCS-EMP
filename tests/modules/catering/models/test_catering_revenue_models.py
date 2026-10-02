"""Tests for the Catering revenue domain model."""

from datetime import date, datetime
from decimal import Decimal

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


def test_catering_revenue_inherits_enterprise_mixins():
    """Verify standard CDCS-EMP persistence and audit fields."""

    revenue = CateringRevenue(
        revenue_reference="REV-TEST-001",
        source_type="CATERING_EVENT",
        source_reference="EVENT-001",
        amount=Decimal("1250.00"),
        currency="USD",
        revenue_date=date(2026, 10, 1),
    )

    assert hasattr(revenue, "created_at")
    assert hasattr(revenue, "updated_at")
    assert hasattr(revenue, "created_by")
    assert hasattr(revenue, "updated_by")
    assert hasattr(revenue, "is_deleted")
    assert hasattr(revenue, "deleted_at")

    assert CateringRevenue.is_deleted.property.columns[0].default.arg is False


def test_catering_revenue_soft_delete_methods_work():
    """Verify standard soft-delete and restore behavior."""

    revenue = CateringRevenue(
        revenue_reference="REV-TEST-002",
        source_type="CATERING_EVENT",
        source_reference="EVENT-002",
        amount=Decimal("2500.00"),
        currency="USD",
        revenue_date=date(2026, 10, 1),
    )

    revenue.soft_delete()

    assert revenue.is_deleted is True
    assert isinstance(revenue.deleted_at, datetime)

    revenue.restore()

    assert revenue.is_deleted is False
    assert revenue.deleted_at is None
