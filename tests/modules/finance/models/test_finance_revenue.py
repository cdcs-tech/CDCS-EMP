"""
Tests for the Finance Revenue domain model.
"""

from datetime import date
from decimal import Decimal

from app.modules.finance.models import FinanceRevenue


def test_finance_revenue_uses_enterprise_mixins():
    """FinanceRevenue uses the standard enterprise model foundation."""

    assert hasattr(FinanceRevenue, "created_at")
    assert hasattr(FinanceRevenue, "updated_at")
    assert hasattr(FinanceRevenue, "created_by")
    assert hasattr(FinanceRevenue, "updated_by")
    assert hasattr(FinanceRevenue, "is_deleted")
    assert hasattr(FinanceRevenue, "deleted_at")
    assert hasattr(FinanceRevenue, "guid")


def test_finance_revenue_has_expected_table_name():
    """FinanceRevenue maps to the Finance revenue table."""

    assert FinanceRevenue.__tablename__ == "finance_revenues"


def test_finance_revenue_has_expected_domain_fields():
    """FinanceRevenue exposes the approved A1.2 domain fields."""

    columns = FinanceRevenue.__table__.columns

    expected = {
        "revenue_reference",
        "contribution_reference",
        "source_type",
        "source_reference",
        "amount",
        "currency",
        "revenue_date",
        "revenue_classification",
        "status",
    }

    assert expected.issubset(set(columns.keys()))


def test_finance_revenue_identity_fields_are_unique():
    """Finance-owned and contribution identities are durable and unique."""

    assert FinanceRevenue.__table__.c.revenue_reference.unique is True
    assert FinanceRevenue.__table__.c.contribution_reference.unique is True


def test_finance_revenue_amount_uses_fixed_precision():
    """Finance revenue amounts use the approved fixed precision."""

    amount_type = FinanceRevenue.__table__.c.amount.type

    assert amount_type.precision == 18
    assert amount_type.scale == 2


def test_finance_revenue_has_no_cross_module_foreign_keys():
    """Finance Revenue has no foreign keys into Catering or other modules."""

    assert list(FinanceRevenue.__table__.foreign_keys) == []


def test_finance_revenue_can_represent_decimal_amount():
    """The domain model accepts Decimal values for monetary amounts."""

    revenue = FinanceRevenue(
        revenue_reference="FIN-REV-0001",
        contribution_reference="CONTRIBUTION-0001",
        source_type="CATERING_REVENUE",
        source_reference="CAT-REV-0001",
        amount=Decimal("1250.50"),
        currency="USD",
        revenue_date=date(2026, 10, 1),
        status="",
    )

    assert revenue.amount == Decimal("1250.50")
    assert revenue.currency == "USD"
    assert revenue.revenue_date == date(2026, 10, 1)


def test_finance_revenue_status_has_no_undocumented_default():
    """
    A1.2 establishes the status field without inventing lifecycle
    values or a default before A1.3.
    """

    assert FinanceRevenue.__table__.c.status.nullable is False
    assert FinanceRevenue.__table__.c.status.default is None
