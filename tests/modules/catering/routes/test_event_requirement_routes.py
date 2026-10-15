"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Event Requirement route tests.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.models.user import User

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


def _requirement_form_data(**overrides):
    """
    Build valid Event Requirement form data.
    """
    data = {
        "description": "Bottled Water",
        "item_reference": "WATER-001",
        "quantity": "100",
        "unit": "bottles",
        "fulfilment_type": "PROCUREMENT",
        "required_by_date": "2026-10-20",
        "notes": "Required for guest service.",
    }
    data.update(overrides)
    return data


def test_create_event_requirement_persists_aggregate(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(
        id=7,
        customer=SimpleNamespace(name="Test Customer"),
        event_date=date(2026, 10, 20),
        attendance=100,
        status="CONFIRMED",
    )

    created = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            pass

        def get(self, event_id):
            assert event_id == 7
            return event

    class FakeRequirementService:
        def __init__(self, **kwargs):
            pass

        def create(self, requirement, *, subject):
            created["requirement"] = requirement
            created["subject"] = subject

            requirement.id = 31

            return requirement

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementService",
        FakeRequirementService,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/create",
        data=_requirement_form_data(),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    requirement = created["requirement"]

    assert requirement.event_id == 7
    assert requirement.description == "Bottled Water"
    assert requirement.item_reference == "WATER-001"
    assert requirement.quantity == Decimal("100")
    assert requirement.unit == "bottles"
    assert requirement.fulfilment_type == "PROCUREMENT"
    assert requirement.required_by_date == date(2026, 10, 20)
    assert requirement.notes == "Required for guest service."
    assert requirement.status == "DRAFT"

    assert created["subject"] is not None


def test_edit_event_requirement_updates_and_redirects(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(
        id=7,
        customer=SimpleNamespace(name="Test Customer"),
        event_date=date(2026, 10, 20),
        attendance=100,
        status="CONFIRMED",
    )

    requirement = SimpleNamespace(
        id=31,
        event_id=7,
        description="Old Requirement",
        item_reference="OLD-001",
        quantity=Decimal("20"),
        unit="units",
        fulfilment_type="INVENTORY",
        required_by_date=date(2026, 10, 19),
        notes="Old notes",
        status="DRAFT",
    )

    updated = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            pass

        def get(self, event_id):
            assert event_id == 7
            return event

    class FakeRequirementRepository:
        def get_by_id(self, requirement_id):
            assert requirement_id == 31
            return requirement

    class FakeRequirementService:
        def __init__(self, **kwargs):
            pass

        def update(self, entity, *, subject):
            updated["requirement"] = entity
            updated["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementService",
        FakeRequirementService,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/edit",
        data=_requirement_form_data(
            description="Updated Bottled Water",
            item_reference="WATER-002",
            quantity="150",
            unit="bottles",
            fulfilment_type="INVENTORY",
            required_by_date="2026-10-21",
            notes="Updated requirement.",
        ),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    updated_requirement = updated["requirement"]

    assert updated_requirement.description == (
        "Updated Bottled Water"
    )
    assert updated_requirement.item_reference == "WATER-002"
    assert updated_requirement.quantity == Decimal("150")
    assert updated_requirement.unit == "bottles"
    assert updated_requirement.fulfilment_type == "INVENTORY"
    assert updated_requirement.required_by_date == date(
        2026,
        10,
        21,
    )
    assert updated_requirement.notes == "Updated requirement."

    assert updated["subject"] is not None


def test_identify_event_requirement_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    requirement = SimpleNamespace(
        id=31,
        event_id=7,
        status="DRAFT",
    )

    delegated = {}

    class FakeRequirementRepository:
        def get_by_id(self, requirement_id):
            assert requirement_id == 31
            return requirement

    class FakeRequirementService:
        def __init__(self, **kwargs):
            pass

        def identify(self, entity, *, subject):
            delegated["requirement"] = entity
            delegated["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementService",
        FakeRequirementService,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/identify",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    assert delegated["requirement"] is requirement
    assert delegated["subject"] is not None


def test_ready_event_requirement_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    requirement = SimpleNamespace(
        id=31,
        event_id=7,
        status="IDENTIFIED",
    )

    delegated = {}

    class FakeRequirementRepository:
        def get_by_id(self, requirement_id):
            assert requirement_id == 31
            return requirement

    class FakeRequirementService:
        def __init__(self, **kwargs):
            pass

        def ready(self, entity, *, subject):
            delegated["requirement"] = entity
            delegated["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementService",
        FakeRequirementService,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/ready",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    assert delegated["requirement"] is requirement
    assert delegated["subject"] is not None


def test_ready_event_requirement_preserves_separate_fulfilment_verifier(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    requirement = SimpleNamespace(
        id=31,
        event_id=7,
        status="IDENTIFIED",
    )

    captured = {}

    class FakeRequirementRepository:
        def get_by_id(self, requirement_id):
            assert requirement_id == 31
            return requirement

    class FakeRequirementService:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def ready(self, entity, *, subject):
            assert entity is requirement
            assert subject is not None
            return entity

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )
    monkeypatch.setattr(
        catering_routes,
        "EventRequirementService",
        FakeRequirementService,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/ready",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    verifier = captured.get("fulfilment_verifier")
    assert isinstance(
        verifier,
        catering_routes.EventRequirementFulfilmentVerifier,
    )


def test_cancel_event_requirement_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    requirement = SimpleNamespace(
        id=31,
        event_id=7,
        status="DRAFT",
    )

    delegated = {}

    class FakeRequirementRepository:
        def get_by_id(self, requirement_id):
            assert requirement_id == 31
            return requirement

    class FakeRequirementService:
        def __init__(self, **kwargs):
            pass

        def cancel(self, entity, *, subject):
            delegated["requirement"] = entity
            delegated["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementService",
        FakeRequirementService,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/cancel",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    assert delegated["requirement"] is requirement
    assert delegated["subject"] is not None


def test_view_event_requirement_rejects_requirement_from_other_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(id=7)

    requirement = SimpleNamespace(
        id=31,
        event_id=99,
    )

    class FakeEventService:
        def __init__(self, **kwargs):
            pass

        def get(self, event_id):
            assert event_id == 7
            return event

    class FakeRequirementRepository:
        def get_by_id(self, requirement_id):
            assert requirement_id == 31
            return requirement

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )

    response = authenticated_client.get(
        "/catering/events/7/requirements/31",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements"
    )


def test_event_requirements_list_filters_by_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(
        id=7,
        customer=SimpleNamespace(name="Test Customer"),
        event_date=date(2026, 10, 20),
        attendance=100,
        status="CONFIRMED",
    )

    requirements = [
        SimpleNamespace(
            id=31,
            event_id=7,
            description="Water",
            item_reference="WATER-001",
            quantity=Decimal("100"),
            unit="bottles",
            fulfilment_type="PROCUREMENT",
            required_by_date=date(2026, 10, 20),
            status="DRAFT",
        )
    ]

    queried = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            pass

        def get(self, event_id):
            assert event_id == 7
            return event

    class FakeRequirementRepository:
        def query(self, options):
            queried["options"] = options
            return requirements

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    monkeypatch.setattr(
        catering_routes,
        "EventRequirementRepository",
        FakeRequirementRepository,
    )

    response = authenticated_client.get(
        "/catering/events/7/requirements",
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert b"Water" in response.data

    assert queried["options"].filters == {
        "event_id": 7,
    }
