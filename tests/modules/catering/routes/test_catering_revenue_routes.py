"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Revenue route tests.
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


def _fake_customer_page():
    return SimpleNamespace(
        items=[
            SimpleNamespace(
                id=1,
                name="SSRC Catering Client",
            ),
        ],
    )


def _fake_event_page():
    return SimpleNamespace(
        items=[
            SimpleNamespace(
                id=1,
                event_date=date(2026, 10, 8),
                status="COMPLETED",
            ),
        ],
    )


def _patch_revenue_form_dependencies(
    monkeypatch,
):
    """
    Patch Customer/Event lookup dependencies used by
    Revenue create/edit routes.
    """

    class FakeCustomerService:
        def paginate(self, options):
            return _fake_customer_page()

    class FakeEventRepository:
        def paginate(self, options):
            return _fake_event_page()

    class FakeEventService:
        repository = FakeEventRepository()

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    monkeypatch.setattr(
        catering_routes,
        "CateringEventService",
        lambda authorization_adapter=None: FakeEventService(),
    )


def test_revenues_requires_authentication(
    client,
):
    response = client.get(
        "/catering/revenues/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_revenues_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/revenues/"
    )

    assert response.status_code == 403


def test_revenues_list_delegates_to_repository(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["revenue-1"],
    )

    captured = {}

    class FakeRepository:
        def paginate(self, options):
            captured["options"] = options
            return result

    class FakeRevenueService:
        repository = FakeRepository()

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/revenues/"
        "?page=2"
        "&page_size=50"
        "&direction=desc"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 50
    assert options.sort_by == "revenue_date"
    assert options.sort_direction == "desc"

    assert captured["template"] == (
        "modules/catering/revenues/index.html"
    )

    assert captured["context"]["revenues"] == [
        "revenue-1"
    ]

    assert captured["context"]["pagination"] is result


def test_create_revenue_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/revenues/create"
    )

    assert response.status_code == 403


def test_create_revenue_renders_form(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _patch_revenue_form_dependencies(monkeypatch)

    captured = {}

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/revenues/create"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/revenues/create.html"
    )

    form = captured["context"]["form"]

    assert form is not None
    assert form.customer_id.choices == [
        (1, "SSRC Catering Client"),
    ]
    assert form.event_id.choices == [
        (
            1,
            "Event #1 — 2026-10-08 — COMPLETED",
        ),
    ]


def test_create_revenue_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _patch_revenue_form_dependencies(monkeypatch)

    created = {}

    class FakeModel:
        def __init__(
            self,
            **kwargs,
        ):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class FakeRepository:
        model = FakeModel

    class FakeRevenueService:
        repository = FakeRepository()

        def create(
            self,
            entity,
            subject=None,
        ):
            created["entity"] = entity
            created["subject"] = subject

            entity.id = 7
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    response = authenticated_client.post(
        "/catering/revenues/create",
        data={
            "revenue_reference": "REV-UAT-001",
            "source_type": "CATERING_EVENT",
            "source_reference": "EVENT-1",
            "customer_id": "1",
            "event_id": "1",
            "amount": "1250.00",
            "currency": "USD",
            "revenue_date": "2026-10-08",
            "revenue_classification": "CATERING_SERVICE",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/revenues/7"
    )

    entity = created["entity"]

    assert entity.revenue_reference == "REV-UAT-001"
    assert entity.source_type == "CATERING_EVENT"
    assert entity.source_reference == "EVENT-1"
    assert entity.customer_id == 1
    assert entity.event_id == 1
    assert entity.amount == Decimal("1250.00")
    assert entity.currency == "USD"
    assert entity.revenue_date == date(2026, 10, 8)
    assert (
        entity.revenue_classification
        == "CATERING_SERVICE"
    )
    assert created["subject"] is not None


def test_view_revenue_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/revenues/1"
    )

    assert response.status_code == 403


def test_view_revenue_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    revenue = SimpleNamespace(
        id=1,
        revenue_reference="REV-UAT-001",
    )

    captured = {}

    class FakeRevenueService:
        def get(self, revenue_id):
            captured["revenue_id"] = revenue_id
            return revenue

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/revenues/1"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["revenue_id"] == 1

    assert captured["template"] == (
        "modules/catering/revenues/view.html"
    )

    assert captured["context"]["revenue"] is revenue


def test_edit_revenue_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/revenues/1/edit"
    )

    assert response.status_code == 403


def test_edit_revenue_renders_form(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _patch_revenue_form_dependencies(monkeypatch)

    revenue = SimpleNamespace(
        id=1,
        revenue_reference="REV-UAT-001",
        source_type="CATERING_EVENT",
        source_reference="EVENT-1",
        customer_id=1,
        event_id=1,
        amount=Decimal("1250.00"),
        currency="USD",
        revenue_date=date(2026, 10, 8),
        revenue_classification="CATERING_SERVICE",
    )

    captured = {}

    class FakeRevenueService:
        def get(self, revenue_id):
            assert revenue_id == 1
            return revenue

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/revenues/1/edit"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/revenues/edit.html"
    )

    assert captured["context"]["revenue"] is revenue
    assert captured["context"]["form"] is not None


def test_edit_revenue_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)
    _patch_revenue_form_dependencies(monkeypatch)

    revenue = SimpleNamespace(
        id=1,
        revenue_reference="REV-UAT-001",
        source_type="CATERING_EVENT",
        source_reference="EVENT-1",
        customer_id=1,
        event_id=1,
        amount=Decimal("1250.00"),
        currency="USD",
        revenue_date=date(2026, 10, 8),
        revenue_classification="OLD",
    )

    captured = {}

    class FakeRevenueService:
        def get(self, revenue_id):
            assert revenue_id == 1
            return revenue

        def update(
            self,
            entity,
            subject=None,
        ):
            captured["revenue"] = entity
            captured["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    response = authenticated_client.post(
        "/catering/revenues/1/edit",
        data={
            "revenue_reference": "REV-UAT-001-EDITED",
            "source_type": "CATERING_EVENT",
            "source_reference": "EVENT-1-EDITED",
            "customer_id": "1",
            "event_id": "1",
            "amount": "1500.00",
            "currency": "USD",
            "revenue_date": "2026-10-09",
            "revenue_classification": "CATERING_SERVICE",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/revenues/1"
    )

    assert captured["revenue"] is revenue
    assert captured["subject"] is not None

    assert revenue.revenue_reference == (
        "REV-UAT-001-EDITED"
    )
    assert revenue.source_type == "CATERING_EVENT"
    assert revenue.source_reference == "EVENT-1-EDITED"
    assert revenue.customer_id == 1
    assert revenue.event_id == 1
    assert revenue.amount == Decimal("1500.00")
    assert revenue.currency == "USD"
    assert revenue.revenue_date == date(2026, 10, 9)
    assert revenue.revenue_classification == (
        "CATERING_SERVICE"
    )


def test_establish_revenue_eligibility_requires_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/revenues/1/establish-eligibility"
    )

    assert response.status_code == 403


def test_establish_revenue_eligibility_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    revenue = SimpleNamespace(
        id=1,
    )

    captured = {}

    class FakeRevenueService:
        def get(self, revenue_id):
            captured["revenue_id"] = revenue_id
            return revenue

        def establish_eligibility(
            self,
            entity,
            subject=None,
        ):
            captured["revenue"] = entity
            captured["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    response = authenticated_client.post(
        "/catering/revenues/1/establish-eligibility",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/revenues/1"
    )

    assert captured["revenue_id"] == 1
    assert captured["revenue"] is revenue
    assert captured["subject"] is not None


def test_recognize_revenue_requires_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/revenues/1/recognize"
    )

    assert response.status_code == 403


def test_recognize_revenue_delegates_to_dispatcher(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context

            return SimpleNamespace(
                success=True,
                message="Catering Revenue recognized successfully.",
            )

    authenticated_client.application.extensions[
        "command_dispatcher"
    ] = FakeDispatcher()

    response = authenticated_client.post(
        "/catering/revenues/1/recognize",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/revenues/1"
    )

    command = captured["command"]
    context = captured["context"]

    assert command.revenue_id == 1
    assert command.__class__.__name__ == (
        "RecognizeCateringRevenueCommand"
    )

    assert context.user_id is not None
    assert context.module_name == "CATERING"
    assert context.operation == (
        "catering.revenue.recognize"
    )


def test_cancel_revenue_requires_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/revenues/1/cancel"
    )

    assert response.status_code == 403


def test_cancel_revenue_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    revenue = SimpleNamespace(
        id=1,
    )

    captured = {}

    class FakeRevenueService:
        def get(self, revenue_id):
            captured["revenue_id"] = revenue_id
            return revenue

        def cancel(
            self,
            entity,
            subject=None,
        ):
            captured["revenue"] = entity
            captured["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CateringRevenueService",
        lambda authorization_adapter=None: FakeRevenueService(),
    )

    response = authenticated_client.post(
        "/catering/revenues/1/cancel",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/revenues/1"
    )

    assert captured["revenue_id"] == 1
    assert captured["revenue"] is revenue
    assert captured["subject"] is not None
