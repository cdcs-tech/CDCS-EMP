"""Route tests for Reporting pages and report execution."""

from decimal import Decimal
from types import SimpleNamespace

from datetime import date

from sqlalchemy.exc import MultipleResultsFound

from app.core.reporting.permissions import ReportPermissionCode
from app.models.user import User
import app.modules.reporting.routes.routes as reporting_routes


def _allow_permissions(monkeypatch):
    """Allow and record permission checks made by Reporting routes."""

    checked_permissions = []

    def allow_permission(self, permission):
        checked_permissions.append(permission)
        return True

    monkeypatch.setattr(User, "has_permission", allow_permission)
    return checked_permissions


def _fake_result():
    """Return a representative result matching the profitability service."""

    return SimpleNamespace(
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


def _stub_event_list(monkeypatch):
    """Avoid database-dependent event-listing behavior in route tests."""

    event = SimpleNamespace(
        id=7,
        event_date="2026-10-26",
        status="COMPLETED",
        service_details="Ministry of ICT workshop",
    )
    monkeypatch.setattr(
        reporting_routes,
        "_get_catering_events",
        lambda: [event],
    )
    return event


def test_reports_landing_page_requires_view_permission(
    authenticated_client,
    monkeypatch,
):
    """The landing page requires Reporting view access."""

    checked_permissions = _allow_permissions(monkeypatch)

    response = authenticated_client.get("/reports/")

    assert response.status_code == 200
    assert b"Reports" in response.data
    assert b"Catering Event Profitability" in response.data
    assert b"Open Report" in response.data
    assert ReportPermissionCode.VIEW in checked_permissions


def test_profitability_report_shows_event_selector(
    authenticated_client,
    monkeypatch,
):
    """The report selector requires execute permission."""

    checked_permissions = _allow_permissions(monkeypatch)
    event = _stub_event_list(monkeypatch)

    response = authenticated_client.get(
        "/reports/catering-event-profitability"
    )

    assert response.status_code == 200
    assert b"Select a Catering Event" in response.data
    assert b"Ministry of ICT workshop" in response.data
    assert str(event.id).encode() in response.data
    # The route must check EXECUTE; VIEW may also be checked by
    # the shared navigation context processor during template rendering.
    assert ReportPermissionCode.EXECUTE in checked_permissions


def test_profitability_report_renders_service_result(
    authenticated_client,
    monkeypatch,
):
    """The route renders values returned by the authoritative service."""

    checked_permissions = _allow_permissions(monkeypatch)
    _stub_event_list(monkeypatch)
    result = _fake_result()
    service_calls = []

    class FakeProfitabilityService:
        def __init__(self, **kwargs):
            service_calls.append(kwargs)

        def calculate_for_event(self, event_id):
            assert event_id == 7
            return result

    monkeypatch.setattr(
        reporting_routes,
        "EventProfitabilityService",
        FakeProfitabilityService,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability?event_id=7"
    )

    assert response.status_code == 200
    assert b"Recognized Revenue" in response.data
    assert b"Consumed Costs" in response.data
    assert b"Profit / (Loss)" in response.data
    assert b"1,250.00" in response.data
    assert b"150.00" in response.data
    assert b"1,100.00" in response.data
    assert b"COST-11" in response.data
    assert len(service_calls) == 1
    assert ReportPermissionCode.EXECUTE in checked_permissions


def test_profitability_report_shows_unavailable_state(
    authenticated_client,
    monkeypatch,
):
    """Missing required data is not represented as zero profit."""

    checked_permissions = _allow_permissions(monkeypatch)
    _stub_event_list(monkeypatch)

    class FakeProfitabilityService:
        def __init__(self, **kwargs):
            pass

        def calculate_for_event(self, event_id):
            raise ValueError(
                "Recognized Catering Revenue not found."
            )

    monkeypatch.setattr(
        reporting_routes,
        "EventProfitabilityService",
        FakeProfitabilityService,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability?event_id=7"
    )

    assert response.status_code == 200
    assert b"Profitability is currently unavailable" in response.data
    assert b"No profitability figure has been calculated" in response.data
    assert b"1,100.00" not in response.data
    assert ReportPermissionCode.EXECUTE in checked_permissions


def test_profitability_report_shows_data_conflict_state(
    authenticated_client,
    monkeypatch,
):
    """Cardinality conflicts are surfaced distinctly from missing data."""

    checked_permissions = _allow_permissions(monkeypatch)
    _stub_event_list(monkeypatch)

    class FakeProfitabilityService:
        def __init__(self, **kwargs):
            pass

        def calculate_for_event(self, event_id):
            raise MultipleResultsFound(
                "Conflicting recognized revenue."
            )

    monkeypatch.setattr(
        reporting_routes,
        "EventProfitabilityService",
        FakeProfitabilityService,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability?event_id=7"
    )

    assert response.status_code == 200
    assert b"Report unavailable due to conflicting data" in response.data
    assert b"Resolve the underlying data issue" in response.data
    assert ReportPermissionCode.EXECUTE in checked_permissions


def test_profitability_report_rejects_invalid_event_id(
    authenticated_client,
    monkeypatch,
):
    """Malformed event IDs do not reach the profitability service."""

    checked_permissions = _allow_permissions(monkeypatch)
    _stub_event_list(monkeypatch)

    def fail_if_called(**kwargs):
        raise AssertionError(
            "The profitability service must not be constructed "
            "for an invalid event ID."
        )

    monkeypatch.setattr(
        reporting_routes,
        "EventProfitabilityService",
        fail_if_called,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability?event_id=invalid"
    )

    assert response.status_code == 400
    assert b"Choose a valid Catering Event" in response.data
    assert ReportPermissionCode.EXECUTE in checked_permissions


def _fake_register_result():
    """Return a representative paginated register result."""

    item = SimpleNamespace(
        event_id=7,
        event_reference="EVENT-7",
        event_date=date(2026, 10, 26),
        customer_name="Ministry of ICT",
        operational_status="COMPLETED",
        financial_readiness="AWAITING DATA",
    )

    return SimpleNamespace(
        items=(item,),
        total_records=1,
        page=1,
        page_size=25,
        total_pages=1,
        has_previous=False,
        has_next=False,
    )


def test_profitability_register_renders_events_and_readiness(
    authenticated_client,
    monkeypatch,
):
    """The register renders event information and financial readiness."""

    checked_permissions = _allow_permissions(monkeypatch)
    monkeypatch.setattr(
        reporting_routes,
        "_get_active_customers",
        lambda: [
            SimpleNamespace(id=3, name="Ministry of ICT"),
        ],
    )

    result = _fake_register_result()
    service_calls = []

    class FakeRegisterService:
        DEFAULT_PAGE_SIZE = 25

        def get_register(self, **kwargs):
            service_calls.append(kwargs)
            return result

    monkeypatch.setattr(
        reporting_routes,
        "CateringEventProfitabilityRegisterService",
        FakeRegisterService,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability-register"
    )

    assert response.status_code == 200
    assert b"Catering Event Profitability Register" in response.data
    assert b"EVENT-7" in response.data
    assert b"Ministry of ICT" in response.data
    assert b"COMPLETED" in response.data
    assert b"AWAITING DATA" in response.data
    assert b"Open Detail" in response.data
    assert len(service_calls) == 1
    assert service_calls[0]["page"] == 1
    assert service_calls[0]["page_size"] == 25
    assert ReportPermissionCode.EXECUTE in checked_permissions


def test_profitability_register_passes_filters_to_service(
    authenticated_client,
    monkeypatch,
):
    """Register filter values are passed to the service unchanged."""

    _allow_permissions(monkeypatch)
    monkeypatch.setattr(
        reporting_routes,
        "_get_active_customers",
        lambda: [
            SimpleNamespace(id=3, name="Ministry of ICT"),
        ],
    )

    service_calls = []

    class FakeRegisterService:
        DEFAULT_PAGE_SIZE = 25

        def get_register(self, **kwargs):
            service_calls.append(kwargs)
            return _fake_register_result()

    monkeypatch.setattr(
        reporting_routes,
        "CateringEventProfitabilityRegisterService",
        FakeRegisterService,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability-register"
        "?date_from=2026-10-01"
        "&date_to=2026-10-31"
        "&operational_status=COMPLETED"
        "&customer_id=3"
        "&page=2"
    )

    assert response.status_code == 200
    assert len(service_calls) == 1
    assert service_calls[0] == {
        "date_from": date(2026, 10, 1),
        "date_to": date(2026, 10, 31),
        "operational_status": "COMPLETED",
        "customer_id": 3,
        "page": 2,
        "page_size": 25,
    }


def test_profitability_register_rejects_invalid_date_range(
    authenticated_client,
    monkeypatch,
):
    """An inverted date range is rejected before service execution."""

    checked_permissions = _allow_permissions(monkeypatch)
    monkeypatch.setattr(
        reporting_routes,
        "_get_active_customers",
        lambda: [],
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "The register service must not run for an invalid date range."
        )

    monkeypatch.setattr(
        reporting_routes,
        "CateringEventProfitabilityRegisterService",
        fail_if_called,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability-register"
        "?date_from=2026-10-31&date_to=2026-10-01"
    )

    assert response.status_code == 400
    assert b"Start date cannot be after end date" in response.data
    assert ReportPermissionCode.EXECUTE in checked_permissions


def test_profitability_register_rejects_invalid_status(
    authenticated_client,
    monkeypatch,
):
    """Unknown operational statuses are rejected."""

    _allow_permissions(monkeypatch)
    monkeypatch.setattr(
        reporting_routes,
        "_get_active_customers",
        lambda: [],
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "The register service must not run for an invalid status."
        )

    monkeypatch.setattr(
        reporting_routes,
        "CateringEventProfitabilityRegisterService",
        fail_if_called,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability-register"
        "?operational_status=NOT_A_REAL_STATUS"
    )

    assert response.status_code == 400
    assert b"Choose a valid operational status" in response.data


def test_profitability_register_rejects_invalid_page(
    authenticated_client,
    monkeypatch,
):
    """Invalid page numbers are rejected before service execution."""

    _allow_permissions(monkeypatch)
    monkeypatch.setattr(
        reporting_routes,
        "_get_active_customers",
        lambda: [],
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "The register service must not run for an invalid page."
        )

    monkeypatch.setattr(
        reporting_routes,
        "CateringEventProfitabilityRegisterService",
        fail_if_called,
    )

    response = authenticated_client.get(
        "/reports/catering-event-profitability-register?page=0"
    )

    assert response.status_code == 400
    assert b"Page must be at least 1" in response.data
