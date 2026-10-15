"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event operational lifecycle route tests.
"""
from app.models.user import User

from types import SimpleNamespace

import app.modules.catering.routes.routes as catering_routes


def _allow_permissions(monkeypatch):
    """
    Explicitly authorize successful route-path tests.
    """
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def _fake_event(event_id=7, status="CONFIRMED"):
    """
    Build a minimal Catering Event test entity.
    """
    return SimpleNamespace(
        id=event_id,
        status=status,
    )


def _assert_operational_route(
    authenticated_client,
    monkeypatch,
    *,
    endpoint,
    service_method,
    initial_status,
):
    """
    Verify an operational Event route delegates to its service method.
    """
    _allow_permissions(monkeypatch)

    event = _fake_event(
        status=initial_status,
    )

    delegated = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            pass

        def get(self, event_id):
            assert event_id == 7
            return event

        def _operation(self, entity, *, subject):
            delegated["event"] = entity
            delegated["subject"] = subject

    setattr(
        FakeEventService,
        service_method,
        FakeEventService._operation,
    )

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    response = authenticated_client.post(
        f"/catering/events/7/{endpoint}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7"
    )

    assert delegated["event"] is event
    assert delegated["subject"] is not None


def test_plan_catering_event_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _assert_operational_route(
        authenticated_client,
        monkeypatch,
        endpoint="plan",
        service_method="plan",
        initial_status="CONFIRMED",
    )


def test_ready_catering_event_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _assert_operational_route(
        authenticated_client,
        monkeypatch,
        endpoint="ready",
        service_method="ready",
        initial_status="PLANNING",
    )


def test_start_production_catering_event_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _assert_operational_route(
        authenticated_client,
        monkeypatch,
        endpoint="start-production",
        service_method="start_production",
        initial_status="READY",
    )


def test_deliver_catering_event_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _assert_operational_route(
        authenticated_client,
        monkeypatch,
        endpoint="deliver",
        service_method="deliver",
        initial_status="IN_PRODUCTION",
    )


def test_complete_catering_event_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _assert_operational_route(
        authenticated_client,
        monkeypatch,
        endpoint="complete",
        service_method="complete",
        initial_status="DELIVERED",
    )


def test_select_catering_request_for_event_filters_submitted_requests(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    request_record = SimpleNamespace(
        id=17,
        request_date="2026-10-11",
        customer=SimpleNamespace(
            name="International Committee of the Red Cross (ICRC)",
        ),
        requested_service="Five-day workshop catering and venue hire",
        service_date="2026-10-19",
        attendance=35,
        status="SUBMITTED",
    )

    pagination = SimpleNamespace(
        items=[request_record],
        page=1,
        page_size=25,
        total_pages=1,
        total_records=1,
        has_previous=False,
        has_next=False,
    )

    captured = {}

    class FakeRequestRepository:
        def paginate(self, options):
            captured["options"] = options
            return pagination

    class FakeCateringRequestService:
        def __init__(self, **kwargs):
            self.repository = FakeRequestRepository()

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeCateringRequestService,
    )

    response = authenticated_client.get(
        "/catering/events/create-from-request",
    )

    assert response.status_code == 200
    assert b"Select Catering Request" in response.data
    assert b"International Committee of the Red Cross (ICRC)" in response.data
    assert b"Create Event" in response.data
    assert b"/catering/requests/17/create-event" in response.data

    options = captured["options"]
    assert options.filters == {"status": "SUBMITTED"}


def test_select_catering_request_for_event_shows_empty_state(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    pagination = SimpleNamespace(
        items=[],
        page=1,
        page_size=25,
        total_pages=0,
        total_records=0,
        has_previous=False,
        has_next=False,
    )

    class FakeRequestRepository:
        def paginate(self, options):
            assert options.filters == {"status": "SUBMITTED"}
            return pagination

    class FakeCateringRequestService:
        def __init__(self, **kwargs):
            self.repository = FakeRequestRepository()

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeCateringRequestService,
    )

    response = authenticated_client.get(
        "/catering/events/create-from-request",
    )

    assert response.status_code == 200
    assert b"No submitted Catering Requests are currently available" in response.data



def test_submit_catering_request_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    """Verify POST submission delegates to the request service."""
    _allow_permissions(monkeypatch)

    catering_request = SimpleNamespace(id=17)
    delegated = {}

    class FakeRequestService:
        def __init__(self, **kwargs):
            pass

        def get(self, request_id):
            assert request_id == 17
            return catering_request

        def submit(self, entity, *, subject):
            delegated["entity"] = entity
            delegated["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeRequestService,
    )

    response = authenticated_client.post(
        "/catering/requests/17/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/requests/17"
    )
    assert delegated["entity"] is catering_request
    assert delegated["subject"] is not None


def test_submit_catering_request_handles_missing_request(
    authenticated_client,
    monkeypatch,
):
    """Verify a missing request redirects to the request list."""
    _allow_permissions(monkeypatch)

    from app.core.crud.exceptions import EntityNotFoundException

    class FakeRequestService:
        def __init__(self, **kwargs):
            pass

        def get(self, request_id):
            raise EntityNotFoundException(
                "Catering Request",
                request_id,
            )

        def submit(self, entity, *, subject):
            raise AssertionError(
                "Submission must not run for a missing request."
            )

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeRequestService,
    )

    response = authenticated_client.post(
        "/catering/requests/17/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/requests/"
    )



def test_submit_catering_request_handles_permission_error(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    class FakeRequestService:
        def __init__(self, authorization_adapter=None):
            pass

        def get(self, request_id):
            return SimpleNamespace(id=request_id)

        def submit(self, catering_request, *, subject):
            raise PermissionError("Submission denied.")

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeRequestService,
    )

    response = authenticated_client.post(
        "/catering/requests/17/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/catering/requests/17")

    with authenticated_client.session_transaction() as session:
        flashes = session.get("_flashes", [])

    assert any(
        "not authorized to submit" in message.lower()
        for category, message in flashes
        if category == "danger"
    )


def test_submit_catering_request_handles_validation_error(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    class FakeRequestService:
        def __init__(self, authorization_adapter=None):
            pass

        def get(self, request_id):
            return SimpleNamespace(id=request_id)

        def submit(self, catering_request, *, subject):
            raise ValueError("Catering Request cannot be submitted in its current state.")

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeRequestService,
    )

    response = authenticated_client.post(
        "/catering/requests/17/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/catering/requests/17")

    with authenticated_client.session_transaction() as session:
        flashes = session.get("_flashes", [])

    assert any(
        "cannot be submitted in its current state" in message.lower()
        for category, message in flashes
        if category == "danger"
    )


def test_create_event_from_request_handles_duplicate_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    class FakeRequestService:
        def __init__(self, authorization_adapter=None):
            pass

        def get(self, request_id):
            return SimpleNamespace(
                id=request_id,
                service_date=None,
                requested_service="UAT Test Workshop",
                attendance=25,
                notes="",
                requirements="",
            )

    class FakeCoordinationService:
        def __init__(self, authorization_adapter=None):
            pass

        def create_event_from_request(
            self,
            request_id,
            *,
            subject,
            event_date=None,
            service_details=None,
            attendance=None,
            operational_notes=None,
        ):
            raise ValueError(
                f"A Catering Event already exists for Catering Request {request_id}."
            )

    monkeypatch.setattr(
        catering_routes,
        "CateringRequestService",
        FakeRequestService,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringRequestEventCoordinationService",
        FakeCoordinationService,
    )

    response = authenticated_client.post(
        "/catering/requests/17/create-event",
        data={
            "event_date": "2026-10-20",
            "service_details": "UAT Test Workshop",
            "attendance": "25",
            "operational_notes": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/requests/17"
    )

    with authenticated_client.session_transaction() as session:
        flashes = session.get("_flashes", [])

    assert any(
        category == "danger"
        and "already exists" in message.lower()
        for category, message in flashes
    )
