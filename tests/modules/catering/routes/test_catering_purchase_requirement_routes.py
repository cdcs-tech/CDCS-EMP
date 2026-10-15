"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Purchase Requirement route tests.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.models.user import User

import app.modules.catering.routes.routes as catering_routes


def _allow_permissions(monkeypatch):
    """Explicitly authorize successful route-path tests."""
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def _event(status="CONFIRMED"):
    return SimpleNamespace(
        id=7,
        customer=SimpleNamespace(name="Test Customer"),
        event_date=date(2026, 10, 20),
        attendance=100,
        status=status,
    )


def _event_requirement(
    fulfilment_type="PROCUREMENT",
    purchase_requirement=None,
):
    return SimpleNamespace(
        id=31,
        event_id=7,
        description="Bottled Water",
        fulfilment_type=fulfilment_type,
        purchase_requirement=purchase_requirement,
    )


def _form_data(**overrides):
    data = {
        "description": "Bottled Water",
        "item_reference": "WATER-001",
        "quantity": "100",
        "unit": "bottles",
        "required_by_date": "2026-10-20",
        "justification": "Required for workshop participants.",
    }
    data.update(overrides)
    return data


def _patch_dependencies(
    monkeypatch,
    *,
    event=None,
    requirement=None,
    created=None,
    submitted=None,
    handoff_error=None,
):
    event = event or _event()
    requirement = requirement or _event_requirement()
    created = created if created is not None else {}
    submitted = submitted if submitted is not None else {}
    transactions = []

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

    class FakePurchaseRequirementRepository:
        def get_by_id(self, purchase_requirement_id):
            assert purchase_requirement_id == 41
            return requirement.purchase_requirement

    class FakeTransaction:
        def __init__(self):
            self.active = False
            self.rolled_back = False
            self.committed = False
            transactions.append(self)

        def begin(self):
            self.active = True

        def commit(self):
            self.active = False
            self.committed = True

        def rollback(self):
            self.active = False
            self.rolled_back = True

    class FakePurchaseRequirementService:
        def __init__(self, **kwargs):
            pass

        def create(self, entity, *, subject):
            created["requirement"] = entity
            created["subject"] = subject
            entity.id = 41
            return entity

    class FakeHandoffService:
        def __init__(self, **kwargs):
            pass

        def submit_to_procurement(self, purchase_requirement, *, subject):
            submitted["requirement"] = purchase_requirement
            submitted["subject"] = subject

            if handoff_error is not None:
                raise handoff_error

            purchase_requirement.procurement_reference = (
                "CATERING-PR-TEST"
            )
            return SimpleNamespace(id=91)

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
        "CateringPurchaseRequirementRepository",
        FakePurchaseRequirementRepository,
    )
    monkeypatch.setattr(
        catering_routes,
        "SQLAlchemyTransactionManager",
        FakeTransaction,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringPurchaseRequirementService",
        FakePurchaseRequirementService,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringProcurementHandoffService",
        FakeHandoffService,
    )

    return {
        "created": created,
        "submitted": submitted,
        "transactions": transactions,
    }


def test_create_purchase_requirement_persists_draft_and_redirects(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    dependencies = _patch_dependencies(monkeypatch)

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/"
        "purchase-requirement/create",
        data=_form_data(),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    purchase_requirement = dependencies["created"]["requirement"]

    assert purchase_requirement.event_requirement_id == 31
    assert purchase_requirement.description == "Bottled Water"
    assert purchase_requirement.item_reference == "WATER-001"
    assert purchase_requirement.quantity == Decimal("100")
    assert purchase_requirement.unit == "bottles"
    assert purchase_requirement.required_by_date == date(
        2026, 10, 20
    )
    assert purchase_requirement.justification == (
        "Required for workshop participants."
    )
    assert purchase_requirement.status == "DRAFT"
    assert purchase_requirement.procurement_reference is None
    assert dependencies["created"]["subject"] is not None


def test_create_purchase_requirement_rejects_inventory_fulfilment(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _patch_dependencies(
        monkeypatch,
        requirement=_event_requirement(
            fulfilment_type="INVENTORY"
        ),
    )

    response = authenticated_client.get(
        "/catering/events/7/requirements/31/"
        "purchase-requirement/create",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )


def test_create_purchase_requirement_rejects_unconfirmed_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _patch_dependencies(
        monkeypatch,
        event=_event(status="DELIVERED"),
    )

    response = authenticated_client.get(
        "/catering/events/7/requirements/31/"
        "purchase-requirement/create",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )


def test_submit_purchase_requirement_to_procurement_succeeds(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    purchase_requirement = SimpleNamespace(
        id=41,
        event_requirement_id=31,
        procurement_reference=None,
    )
    requirement = _event_requirement(
        purchase_requirement=purchase_requirement,
    )

    dependencies = _patch_dependencies(
        monkeypatch,
        requirement=requirement,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/"
        "purchase-requirement/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )

    submitted = dependencies["submitted"]

    assert submitted["requirement"] is purchase_requirement
    assert submitted["subject"] is not None
    assert purchase_requirement.procurement_reference == (
        "CATERING-PR-TEST"
    )

    assert len(dependencies["transactions"]) == 1
    assert dependencies["transactions"][0].committed is True
    assert dependencies["transactions"][0].rolled_back is False


def test_submit_purchase_requirement_rejects_mismatched_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    purchase_requirement = SimpleNamespace(
        id=41,
        event_requirement_id=31,
        procurement_reference=None,
    )
    requirement = _event_requirement(
        purchase_requirement=purchase_requirement,
    )
    requirement.event_id = 99

    dependencies = _patch_dependencies(
        monkeypatch,
        requirement=requirement,
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/"
        "purchase-requirement/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )
    assert "requirement" not in dependencies["submitted"]
    assert dependencies["transactions"] == []


def test_submit_purchase_requirement_rolls_back_on_handoff_failure(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    purchase_requirement = SimpleNamespace(
        id=41,
        event_requirement_id=31,
        procurement_reference=None,
    )
    requirement = _event_requirement(
        purchase_requirement=purchase_requirement,
    )

    dependencies = _patch_dependencies(
        monkeypatch,
        requirement=requirement,
        handoff_error=RuntimeError("Simulated handoff failure"),
    )

    response = authenticated_client.post(
        "/catering/events/7/requirements/31/"
        "purchase-requirement/submit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7/requirements/31"
    )
    assert dependencies["submitted"]["requirement"] is (
        purchase_requirement
    )
    assert purchase_requirement.procurement_reference is None

    assert len(dependencies["transactions"]) == 1
    assert dependencies["transactions"][0].rolled_back is True
    assert dependencies["transactions"][0].committed is False
    assert dependencies["transactions"][0].active is False
