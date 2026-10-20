"""Browser route tests for Catering Event Profitability."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from app.models.user import User
import app.modules.catering.routes.routes as catering_routes
from sqlalchemy.exc import MultipleResultsFound
from app.modules.catering.services.event_profitability import (
    EventProfitabilityResult,
)


def _allow_permissions(monkeypatch):
    """Explicitly authorize successful route-path tests."""

    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def _fake_event(event_id=7, status="CONFIRMED"):
    """Return the minimal event object required by the detail route."""

    return SimpleNamespace(
        id=event_id,
        status=status,
    )


def _profitability_result():
    """Build a representative result from the existing read-only service."""

    return EventProfitabilityResult(
        event_id=7,
        event_reference="EVENT-7",
        revenue_reference="REV-7",
        revenue_amount=Decimal("1250.00"),
        currency="USD",
        cost_contributions=(
            SimpleNamespace(
                association_id=11,
                contribution_id="COST-11",
                expense_id=21,
                expense_amount=Decimal("150.00"),
            ),
        ),
        total_cost=Decimal("150.00"),
        profit=Decimal("1100.00"),
    )


def _configure_event_detail(
    monkeypatch,
    *,
    profitability_result=None,
    profitability_error=None,
    associations=None,
    expenses_by_id=None,
):
    """Stub Event detail dependencies and capture template context."""

    catering_event = _fake_event()
    associations = list(associations or [])
    expenses_by_id = dict(expenses_by_id or {})

    monkeypatch.setattr(
        catering_routes.CateringEventService,
        "get",
        lambda self, event_id: catering_event,
    )
    monkeypatch.setattr(
        catering_routes.CateringQuotationRepository,
        "get_accepted_by_event_id",
        lambda self, event_id: None,
    )

    class FakeAssociationRepository:
        def get_by_catering_context(
            self,
            catering_context_type,
            catering_context_reference,
        ):
            assert catering_context_type == "CATERING_EVENT"
            assert catering_context_reference == "EVENT-7"
            return associations

    class FakeExpenseRepository:
        def get_by_id(self, expense_id):
            return expenses_by_id.get(expense_id)

    monkeypatch.setattr(
        catering_routes,
        "CateringExpenseCostAssociationRepository",
        FakeAssociationRepository,
    )
    monkeypatch.setattr(
        catering_routes,
        "ExpenseRepository",
        FakeExpenseRepository,
    )

    profitability_service = Mock()

    if profitability_error is not None:
        profitability_service.calculate_for_event.side_effect = (
            profitability_error
        )
    else:
        profitability_service.calculate_for_event.return_value = (
            profitability_result
        )

    monkeypatch.setattr(
        catering_routes,
        "EventProfitabilityService",
        Mock(return_value=profitability_service),
    )

    render_template_mock = Mock(return_value="event-detail-response")
    monkeypatch.setattr(
        catering_routes,
        "render_template",
        render_template_mock,
    )

    return catering_event, profitability_service, render_template_mock


def test_event_detail_passes_profitability_result_to_template(
    authenticated_client,
    monkeypatch,
):
    """The event detail route passes the existing service result to its template."""

    _allow_permissions(monkeypatch)
    result = _profitability_result()

    event, profitability_service, render_template_mock = (
        _configure_event_detail(
            monkeypatch,
            profitability_result=result,
        )
    )

    response = authenticated_client.get("/catering/events/7")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "event-detail-response"

    profitability_service.calculate_for_event.assert_called_once_with(
        event.id
    )

    render_template_mock.assert_called_once()
    assert (
        render_template_mock.call_args.args[0]
        == "modules/catering/events/view.html"
    )

    context = render_template_mock.call_args.kwargs
    assert context["catering_event"] is event
    assert context["accepted_quotation"] is None
    assert context["profitability_result"] is result
    assert context["profitability_unavailable"] is False
    assert context["profitability_data_conflict"] is False


def test_event_detail_handles_unavailable_profitability(
    authenticated_client,
    monkeypatch,
):
    """Missing revenue or cost data does not break the event detail page."""

    _allow_permissions(monkeypatch)

    event, profitability_service, render_template_mock = (
        _configure_event_detail(
            monkeypatch,
            profitability_error=ValueError(
                "Recognized Catering revenue is unavailable."
            ),
        )
    )

    response = authenticated_client.get("/catering/events/7")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "event-detail-response"

    profitability_service.calculate_for_event.assert_called_once_with(
        event.id
    )

    context = render_template_mock.call_args.kwargs
    assert context["catering_event"] is event
    assert context["profitability_result"] is None
    assert context["profitability_unavailable"] is True
    assert context["profitability_data_conflict"] is False


def test_event_detail_preserves_event_context_when_profitability_is_unavailable(
    authenticated_client,
    monkeypatch,
):
    """Profitability errors leave the regular event-detail context intact."""

    _allow_permissions(monkeypatch)

    event, _, render_template_mock = _configure_event_detail(
        monkeypatch,
        profitability_error=ValueError(
            "A consumed expense record is unavailable."
        ),
    )

    response = authenticated_client.get("/catering/events/7")

    assert response.status_code == 200

    context = render_template_mock.call_args.kwargs
    assert context["catering_event"] is event
    assert context["accepted_quotation"] is None
    assert context["profitability_result"] is None
    assert context["profitability_unavailable"] is True
    assert context["profitability_data_conflict"] is False


def test_event_detail_handles_multiple_recognized_revenue_records(
    authenticated_client,
    monkeypatch,
):
    """A revenue cardinality conflict must not break event detail."""

    _allow_permissions(monkeypatch)

    event, profitability_service, render_template_mock = (
        _configure_event_detail(
            monkeypatch,
            profitability_error=MultipleResultsFound(
                "Multiple recognized revenue records found."
            ),
        )
    )

    response = authenticated_client.get("/catering/events/7")

    assert response.status_code == 200
    assert response.get_data(as_text=True) == "event-detail-response"

    profitability_service.calculate_for_event.assert_called_once_with(
        event.id
    )

    context = render_template_mock.call_args.kwargs
    assert context["catering_event"] is event
    assert context["profitability_result"] is None
    assert context["profitability_unavailable"] is True
    assert context["profitability_data_conflict"] is True


def test_event_detail_passes_eligible_expense_association_to_template(
    authenticated_client,
    monkeypatch,
):
    """Eligible associations remain visible independently of profitability."""

    _allow_permissions(monkeypatch)

    association = SimpleNamespace(
        id=1,
        expense_id=21,
        status="ELIGIBLE",
        consumed_at=None,
        catering_context_type="CATERING_EVENT",
        catering_context_reference="EVENT-7",
    )
    expense = SimpleNamespace(
        id=21,
        description="Workshop catering ingredients",
        amount=Decimal("420.00"),
        expense_date=date(2026, 10, 26),
    )

    event, _, render_template_mock = _configure_event_detail(
        monkeypatch,
        profitability_error=ValueError(
            "Recognized Catering revenue is unavailable."
        ),
        associations=[association],
        expenses_by_id={21: expense},
    )

    response = authenticated_client.get("/catering/events/7")

    assert response.status_code == 200

    context = render_template_mock.call_args.kwargs
    assert context["catering_event"] is event
    assert context["profitability_unavailable"] is True
    assert context["expense_cost_association_rows"] == [
        {
            "association": association,
            "expense": expense,
        }
    ]


def test_event_detail_preserves_association_when_expense_is_unavailable(
    authenticated_client,
    monkeypatch,
):
    """An association remains visible when its Expense cannot be resolved."""

    _allow_permissions(monkeypatch)

    association = SimpleNamespace(
        id=2,
        expense_id=99,
        status="ELIGIBLE",
        consumed_at=None,
        catering_context_type="CATERING_EVENT",
        catering_context_reference="EVENT-7",
    )

    _, _, render_template_mock = _configure_event_detail(
        monkeypatch,
        associations=[association],
        expenses_by_id={},
    )

    response = authenticated_client.get("/catering/events/7")

    assert response.status_code == 200

    rows = render_template_mock.call_args.kwargs[
        "expense_cost_association_rows"
    ]
    assert len(rows) == 1
    assert rows[0]["association"] is association
    assert rows[0]["expense"] is None
