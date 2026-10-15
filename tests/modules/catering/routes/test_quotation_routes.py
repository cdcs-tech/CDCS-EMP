"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Quotation route tests.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.models.user import User

from app.core.crud.exceptions import EntityValidationException

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


def _quotation_form_data(**overrides):
    """
    Build valid parent quotation form data.
    """
    data = {
        "quotation_date": "2026-10-07",
        "valid_until": "2026-10-14",
        "adjustment_amount": "25.00",
        "customer_notes": "Quotation prepared for UAT.",
    }
    data.update(overrides)
    return data


def _line_form_data(prefix, **overrides):
    """
    Build valid data for one quotation line.
    """
    data = {
        f"{prefix}-description": "Buffet Catering",
        f"{prefix}-item_reference": "CAT-001",
        f"{prefix}-quantity": "10",
        f"{prefix}-unit": "persons",
        f"{prefix}-unit_price": "50.00",
        f"{prefix}-notes": "Standard buffet package.",
    }
    data.update(overrides)
    return data


def test_create_quotation_from_event_persists_aggregate(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(
        id=7,
        customer_id=11,
    )

    created = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            pass

        def get(self, event_id):
            assert event_id == 7
            return event

    class FakeQuotationService:
        def create(self, quotation, *, subject):
            created["quotation"] = quotation
            created["subject"] = subject

            quotation.id = 21
            quotation.subtotal = Decimal("500.00")
            quotation.total_amount = Decimal("525.00")

            for line in quotation.lines:
                line.total_amount = (
                    line.quantity * line.unit_price
                )

            return quotation

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationService",
        lambda **kwargs: FakeQuotationService(),
    )

    response = authenticated_client.post(
        "/catering/events/7/create-quotation",
        data={
            **_quotation_form_data(),
            **_line_form_data("line-0"),
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/quotations/21"
    )

    quotation = created["quotation"]

    assert quotation.customer_id == 11
    assert quotation.event_id == 7
    assert quotation.quotation_date == date(2026, 10, 7)
    assert quotation.valid_until == date(2026, 10, 14)
    assert quotation.adjustment_amount == Decimal("25.00")
    assert quotation.customer_notes == (
        "Quotation prepared for UAT."
    )

    assert len(quotation.lines) == 1

    line = quotation.lines[0]

    assert line.description == "Buffet Catering"
    assert line.item_reference == "CAT-001"
    assert line.quantity == Decimal("10")
    assert line.unit == "persons"
    assert line.unit_price == Decimal("50.00")
    assert line.notes == "Standard buffet package."

    assert created["subject"] is not None


def test_edit_quotation_replaces_lines_and_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    existing_line = SimpleNamespace(
        description="Old Catering Package",
        item_reference="OLD-001",
        quantity=Decimal("5"),
        unit="persons",
        unit_price=Decimal("40.00"),
        notes="Old notes",
    )

    quotation = SimpleNamespace(
        id=21,
        customer_id=11,
        event_id=7,
        quotation_date=date(2026, 10, 7),
        valid_until=date(2026, 10, 14),
        adjustment_amount=Decimal("0.00"),
        customer_notes="Original quotation.",
        lines=[existing_line],
    )

    updated = {}

    class FakeQuotationService:
        def get(self, quotation_id):
            assert quotation_id == 21
            return quotation

        def update(self, entity, *, subject):
            updated["quotation"] = entity
            updated["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationService",
        lambda **kwargs: FakeQuotationService(),
    )

    response = authenticated_client.post(
        "/catering/quotations/21/edit",
        data={
            **_quotation_form_data(
                quotation_date="2026-10-08",
                valid_until="2026-10-20",
                adjustment_amount="15.00",
                customer_notes="Updated quotation.",
            ),
            **_line_form_data(
                "line-0",
                **{
                    "line-0-description": "Updated Buffet",
                    "line-0-item_reference": "NEW-001",
                    "line-0-quantity": "12",
                    "line-0-unit": "persons",
                    "line-0-unit_price": "55.00",
                    "line-0-notes": "Updated notes",
                },
            ),
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/quotations/21"
    )

    updated_quotation = updated["quotation"]

    assert updated_quotation.quotation_date == date(
        2026,
        10,
        8,
    )
    assert updated_quotation.valid_until == date(
        2026,
        10,
        20,
    )
    assert updated_quotation.adjustment_amount == Decimal(
        "15.00"
    )
    assert updated_quotation.customer_notes == (
        "Updated quotation."
    )

    assert len(updated_quotation.lines) == 1

    line = updated_quotation.lines[0]

    assert line.description == "Updated Buffet"
    assert line.item_reference == "NEW-001"
    assert line.quantity == Decimal("12")
    assert line.unit == "persons"
    assert line.unit_price == Decimal("55.00")
    assert line.notes == "Updated notes"

    assert updated["subject"] is not None


def test_accept_catering_quotation_progresses_associated_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    quotation = SimpleNamespace(
        id=21,
        event_id=7,
        customer_id=11,
        status="ISSUED",
    )
    accepted = {}
    progressed = {}

    class FakeQuotationService:
        def __init__(self, **kwargs):
            pass

        def get(self, quotation_id):
            assert quotation_id == 21
            return quotation

        def accept(self, entity, *, subject):
            assert entity is quotation
            accepted["quotation"] = entity
            accepted["subject"] = subject
            entity.status = "ACCEPTED"
            return entity

    class FakeCoordinationService:
        def __init__(self, **kwargs):
            progressed["kwargs"] = kwargs

        def progress_event_from_accepted_quotation(
            self,
            quotation_id,
            *,
            subject,
        ):
            assert quotation_id == 21
            assert quotation.status == "ACCEPTED"
            progressed["quotation_id"] = quotation_id
            progressed["subject"] = subject
            return SimpleNamespace(id=7, status="QUOTED")

    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationService",
        FakeQuotationService,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationEventCoordinationService",
        FakeCoordinationService,
    )
    monkeypatch.setattr(
        catering_routes,
        "_build_catering_authorization_adapter",
        lambda: object(),
    )

    response = authenticated_client.post(
        "/catering/quotations/21/accept",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/quotations/21"
    )
    assert accepted["quotation"] is quotation
    assert accepted["subject"] is not None
    assert quotation.status == "ACCEPTED"
    assert progressed["quotation_id"] == 21
    assert progressed["subject"] is accepted["subject"]
    assert progressed["kwargs"]["quotation_repository"] is not None
    assert progressed["kwargs"]["event_repository"] is not None
    assert progressed["kwargs"]["authorization_adapter"] is not None


def test_accept_catering_quotation_warns_when_event_progression_fails(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    quotation = SimpleNamespace(
        id=22,
        event_id=8,
        customer_id=12,
        status="ISSUED",
    )

    class FakeQuotationService:
        def __init__(self, **kwargs):
            pass

        def get(self, quotation_id):
            assert quotation_id == 22
            return quotation

        def accept(self, entity, *, subject):
            entity.status = "ACCEPTED"
            return entity

    class FakeCoordinationService:
        def __init__(self, **kwargs):
            pass

        def progress_event_from_accepted_quotation(
            self,
            quotation_id,
            *,
            subject,
        ):
            assert quotation_id == 22
            assert quotation.status == "ACCEPTED"
            raise EntityValidationException(
                "Event is not in REQUESTED status."
            )

    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationService",
        FakeQuotationService,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationEventCoordinationService",
        FakeCoordinationService,
    )
    monkeypatch.setattr(
        catering_routes,
        "_build_catering_authorization_adapter",
        lambda: object(),
    )

    response = authenticated_client.post(
        "/catering/quotations/22/accept",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/quotations/22"
    )
    assert quotation.status == "ACCEPTED"

    with authenticated_client.session_transaction() as session:
        flashes = session.get("_flashes", [])

    assert any(
        category == "warning"
        and "could not be progressed to QUOTED" in message
        and "Event is not in REQUESTED status." in message
        for category, message in flashes
    )


def test_quote_catering_event_progresses_from_accepted_quotation(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    quotation = SimpleNamespace(
        id=21,
        event_id=7,
        status="ACCEPTED",
    )

    retrieved = {}
    progressed = {}

    class FakeQuotationRepository:
        def get_accepted_by_event_id(self, event_id):
            assert event_id == 7
            retrieved["quotation"] = quotation
            return quotation

    class FakeCoordinationService:
        def __init__(self, **kwargs):
            retrieved["kwargs"] = kwargs

        def progress_event_from_accepted_quotation(
            self,
            quotation_id,
            *,
            subject,
        ):
            progressed["quotation_id"] = quotation_id
            progressed["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationRepository",
        FakeQuotationRepository,
    )
    monkeypatch.setattr(
        catering_routes,
        "CateringQuotationEventCoordinationService",
        FakeCoordinationService,
    )

    response = authenticated_client.post(
        "/catering/events/7/quote",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7"
    )
    assert retrieved["quotation"] is quotation
    assert progressed["quotation_id"] == 21
    assert progressed["subject"] is not None


def test_request_confirmation_catering_event_progresses_quoted_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(
        id=7,
        status="QUOTED",
    )

    retrieved = {}
    progressed = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            retrieved["kwargs"] = kwargs

        def get(self, event_id):
            assert event_id == 7
            retrieved["event"] = event
            return event

        def request_confirmation(
            self,
            catering_event,
            *,
            subject,
        ):
            progressed["event"] = catering_event
            progressed["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    response = authenticated_client.post(
        "/catering/events/7/request-confirmation",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7"
    )

    assert retrieved["event"] is event
    assert progressed["event"] is event
    assert progressed["subject"] is not None

def test_confirm_catering_event_progresses_pending_confirmation_event(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    event = SimpleNamespace(
        id=7,
        status="PENDING_CONFIRMATION",
    )

    retrieved = {}
    progressed = {}

    class FakeEventService:
        def __init__(self, **kwargs):
            retrieved["kwargs"] = kwargs

        def get(self, event_id):
            assert event_id == 7
            retrieved["event"] = event
            return event

        def confirm(
            self,
            catering_event,
            *,
            subject,
        ):
            progressed["event"] = catering_event
            progressed["subject"] = subject

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        FakeEventService,
    )

    response = authenticated_client.post(
        "/catering/events/7/confirm",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/events/7"
    )

    assert retrieved["event"] is event
    assert progressed["event"] is event
    assert progressed["subject"] is not None
