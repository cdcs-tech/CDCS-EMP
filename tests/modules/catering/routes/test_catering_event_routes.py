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
