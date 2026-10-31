"""Tests for the Catering Event Profitability Register service."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.dialects import mssql
from sqlalchemy.exc import MultipleResultsFound

from app.modules.reporting.services.catering_event_profitability_register import (
    CateringEventProfitabilityRegisterService,
    READINESS_AWAITING_DATA,
    READINESS_DATA_CONFLICT,
    READINESS_REPORTABLE,
)
from app.modules.reporting.services import (
    catering_event_profitability_register as register_module,
)


def _event():
    return SimpleNamespace(
        id=7,
        event_date=date(2026, 10, 26),
        status="COMPLETED",
    )


def _association():
    return SimpleNamespace(
        id=11,
        expense_id=21,
        is_deleted=False,
    )


def _expense(**overrides):
    values = {
        "id": 21,
        "amount": Decimal("150.00"),
        "is_deleted": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _service(
    *,
    revenue=None,
    associations=None,
    expense=None,
    profitability_result=None,
):
    revenue_repository = Mock()
    revenue_repository.get_recognized_by_event_id.return_value = revenue

    association_repository = Mock()
    association_repository.get_consumed_by_catering_context.return_value = (
        associations or []
    )

    expense_repository = Mock()
    expense_repository.get_by_id.return_value = expense

    profitability_service = Mock()
    profitability_service.calculate_for_event.return_value = (
        profitability_result
    )

    service = CateringEventProfitabilityRegisterService(
        revenue_repository=revenue_repository,
        association_repository=association_repository,
        expense_repository=expense_repository,
        profitability_service=profitability_service,
    )

    return (
        service,
        revenue_repository,
        association_repository,
        expense_repository,
        profitability_service,
    )


def _revenue():
    return SimpleNamespace(
        revenue_reference="REV-7",
        amount=Decimal("1250.00"),
        currency="USD",
        is_deleted=False,
    )


def test_missing_recognized_revenue_is_awaiting_data():
    service, _, _, _, profitability = _service()

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_AWAITING_DATA
    assert row.recognized_revenue is None
    assert row.consumed_costs is None
    assert row.profit_or_loss is None
    profitability.calculate_for_event.assert_not_called()


def test_no_consumed_costs_is_awaiting_data():
    service, _, _, _, profitability = _service(
        revenue=_revenue(),
        associations=[],
    )

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_AWAITING_DATA
    assert row.recognized_revenue is None
    assert row.profit_or_loss is None
    profitability.calculate_for_event.assert_not_called()


def test_missing_linked_expense_is_data_conflict():
    service, _, _, _, profitability = _service(
        revenue=_revenue(),
        associations=[_association()],
        expense=None,
    )

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_DATA_CONFLICT
    assert row.profit_or_loss is None
    profitability.calculate_for_event.assert_not_called()


def test_soft_deleted_linked_expense_is_data_conflict():
    service, _, _, _, profitability = _service(
        revenue=_revenue(),
        associations=[_association()],
        expense=_expense(is_deleted=True),
    )

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_DATA_CONFLICT
    assert row.profit_or_loss is None
    profitability.calculate_for_event.assert_not_called()


def test_missing_expense_currency_is_awaiting_data():
    service, _, _, _, profitability = _service(
        revenue=_revenue(),
        associations=[_association()],
        expense=_expense(),
    )

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_AWAITING_DATA
    assert row.recognized_revenue is None
    assert row.consumed_costs is None
    assert row.profit_or_loss is None
    assert row.currency is None
    profitability.calculate_for_event.assert_not_called()


def test_duplicate_recognized_revenue_is_data_conflict():
    service, revenue_repository, _, _, profitability = _service()

    revenue_repository.get_recognized_by_event_id.side_effect = (
        MultipleResultsFound("Duplicate recognized revenue")
    )

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_DATA_CONFLICT
    assert row.profit_or_loss is None
    profitability.calculate_for_event.assert_not_called()


def test_verified_currency_evidence_uses_authoritative_profitability_service():
    result = SimpleNamespace(
        revenue_amount=Decimal("1250.00"),
        total_cost=Decimal("150.00"),
        profit=Decimal("1100.00"),
        currency="USD",
    )

    service, _, _, _, profitability = _service(
        revenue=_revenue(),
        associations=[_association()],
        expense=_expense(currency="USD"),
        profitability_result=result,
    )

    row = service._build_row(_event(), "Ministry of ICT")

    assert row.financial_readiness == READINESS_REPORTABLE
    assert row.recognized_revenue == Decimal("1250.00")
    assert row.consumed_costs == Decimal("150.00")
    assert row.profit_or_loss == Decimal("1100.00")
    assert row.currency == "USD"
    profitability.calculate_for_event.assert_called_once_with(7)


def _register_event(event_id, status="COMPLETED"):
    return SimpleNamespace(
        id=event_id,
        event_date=date(2026, 10, 26),
        status=status,
    )


def test_register_includes_events_when_customer_is_missing_or_deleted():
    """The query retains events without an active matching customer."""

    captured = {}

    def execute(statement):
        compiled = statement.compile(
            dialect=mssql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
        captured["sql"] = str(compiled)

        if "count(" in captured["sql"].lower():
            return SimpleNamespace(scalar_one=lambda: 2)

        return SimpleNamespace(
            all=lambda: [
                (_register_event(7), None),
                (_register_event(8), None),
            ]
        )

    with patch.object(
        register_module.db.session,
        "execute",
        side_effect=execute,
    ):
        service, *_ = _service()
        result = service.get_register()

    sql = captured["sql"].lower()

    assert "left outer join" in sql
    assert "catering_events.is_deleted = 0" in sql
    assert "customers.is_deleted = 0" in sql
    assert "catering_events.is_deleted is 0" not in sql
    assert "customers.is_deleted is 0" not in sql
    assert "where customers.is_deleted" not in sql

    assert result.total_records == 2
    assert [item.customer_name for item in result.items] == [
        "Customer unavailable",
        "Customer unavailable",
    ]


def test_register_includes_all_operational_statuses():
    """The register query does not restrict the event status."""

    statuses = (
        "REQUESTED",
        "QUOTED",
        "PENDING_CONFIRMATION",
        "CONFIRMED",
        "PLANNING",
        "READY",
        "IN_PRODUCTION",
        "DELIVERED",
        "COMPLETED",
        "CANCELLED",
    )

    events = [
        (_register_event(index + 1, status), "Customer")
        for index, status in enumerate(statuses)
    ]

    def execute(statement):
        compiled = str(
            statement.compile(
                compile_kwargs={"literal_binds": True}
            )
        ).lower()

        if "count(" in compiled:
            return SimpleNamespace(scalar_one=lambda: len(events))

        return SimpleNamespace(all=lambda: events)

    with patch.object(
        register_module.db.session,
        "execute",
        side_effect=execute,
    ):
        service, *_ = _service()
        result = service.get_register()

    assert result.total_records == len(statuses)
    assert {
        item.operational_status for item in result.items
    } == set(statuses)


def test_register_applies_date_status_and_customer_filters():
    """The register query applies each supplied filter."""

    captured = []

    def execute(statement):
        compiled = statement.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled).lower()
        captured.append(sql)

        if "count(" in sql:
            return SimpleNamespace(scalar_one=lambda: 0)

        return SimpleNamespace(all=lambda: [])

    with patch.object(
        register_module.db.session,
        "execute",
        side_effect=execute,
    ):
        service, *_ = _service()
        result = service.get_register(
            date_from=date(2026, 10, 1),
            date_to=date(2026, 10, 31),
            operational_status="COMPLETED",
            customer_id=3,
        )

    assert result.total_records == 0
    assert len(captured) == 2

    for sql in captured:
        assert "catering_events.event_date >=" in sql
        assert "catering_events.event_date <=" in sql
        assert "catering_events.status =" in sql
        assert "catering_events.customer_id =" in sql


def test_register_uses_deterministic_sort_and_bounded_pagination():
    """The register sorts by event date and ID and applies page bounds."""

    captured = []

    def execute(statement):
        compiled = statement.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql = str(compiled).lower()
        captured.append(sql)

        if "count(" in sql:
            return SimpleNamespace(scalar_one=lambda: 61)

        return SimpleNamespace(all=lambda: [])

    with patch.object(
        register_module.db.session,
        "execute",
        side_effect=execute,
    ):
        service, *_ = _service()
        result = service.get_register(page=2, page_size=25)

    page_sql = captured[-1]

    assert (
        "order by catering_events.event_date desc, catering_events.id desc"
        in page_sql
    )
    assert "limit 25" in page_sql
    assert "offset 25" in page_sql

    assert result.total_records == 61
    assert result.page == 2
    assert result.page_size == 25
    assert result.total_pages == 3
    assert result.has_previous is True
    assert result.has_next is True


def test_register_rejects_page_size_above_maximum():
    """The register does not permit unbounded page sizes."""

    service, *_ = _service()

    with pytest.raises(ValueError, match="Page size"):
        service.get_register(page_size=101)
