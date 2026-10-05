"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Customer route tests.
"""

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


def test_customers_requires_authentication(client):
    response = client.get(
        "/catering/customers/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_customers_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/customers/"
    )

    assert response.status_code == 403


def test_customers_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["customer-1"],
    )

    captured = {}

    class FakeCustomerService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            assert options.sort_by == "name"
            assert options.sort_direction == "asc"
            assert options.search is None
            assert options.filters == {
                "is_active": True,
            }
            return result

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/customers/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/customers/index.html"
    )

    assert captured["context"]["customers"] == [
        "customer-1"
    ]

    assert captured["context"]["pagination"] is result


def test_customers_supports_controlled_query_options(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeCustomerService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/catering/customers/"
        "?page=2"
        "&page_size=50"
        "&sort=email"
        "&direction=desc"
        "&search=John"
        "&status=inactive"
    )

    assert response.status_code == 200

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 50
    assert options.sort_by == "email"
    assert options.sort_direction == "desc"
    assert options.search == "John"
    assert options.filters == {
        "is_active": False,
    }


def test_create_customer_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/customers/create"
    )

    assert response.status_code == 403


def test_create_customer_renders_form(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/customers/create"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/customers/create.html"
    )

    assert captured["context"]["form"] is not None


def test_create_customer_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    created = {}

    class FakeModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class FakeRepository:
        model = FakeModel

    class FakeCustomerService:
        repository = FakeRepository()

        def create(self, entity):
            created["entity"] = entity
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    response = authenticated_client.post(
        "/catering/customers/create",
        data={
            "name": "Juba Catering Client",
            "customer_type": "ORGANIZATION",
            "phone": "+211900000000",
            "email": "client@example.com",
            "address": "Juba",
            "notes": "UAT customer",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/customers/"
    )

    entity = created["entity"]

    assert entity.name == "Juba Catering Client"
    assert entity.customer_type == "ORGANIZATION"
    assert entity.phone == "+211900000000"
    assert entity.email == "client@example.com"
    assert entity.address == "Juba"
    assert entity.notes == "UAT customer"


def test_view_customer_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/customers/1"
    )

    assert response.status_code == 403


def test_view_customer_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    customer = SimpleNamespace(
        id=1,
        name="Juba Catering Client",
    )

    captured = {}

    class FakeCustomerService:
        def get(self, customer_id):
            captured["customer_id"] = customer_id
            return customer

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/customers/1"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["customer_id"] == 1
    assert captured["template"] == (
        "modules/catering/customers/view.html"
    )
    assert captured["context"]["customer"] is customer


def test_edit_customer_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/customers/1/edit"
    )

    assert response.status_code == 403


def test_edit_customer_renders_form(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    customer = SimpleNamespace(
        id=1,
        name="Existing Customer",
        customer_type="ORGANIZATION",
        phone="123",
        email="existing@example.com",
        address="Juba",
        notes="Existing",
    )

    captured = {}

    class FakeCustomerService:
        def get(self, customer_id):
            assert customer_id == 1
            return customer

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/customers/1/edit"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/customers/edit.html"
    )
    assert captured["context"]["customer"] is customer
    assert captured["context"]["form"] is not None


def test_edit_customer_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    customer = SimpleNamespace(
        id=1,
        name="Existing Customer",
        customer_type="ORGANIZATION",
        phone="123",
        email="existing@example.com",
        address="Juba",
        notes="Existing",
    )

    captured = {}

    class FakeCustomerService:
        def get(self, customer_id):
            assert customer_id == 1
            return customer

        def update(self, entity):
            captured["customer"] = entity
            return entity

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    response = authenticated_client.post(
        "/catering/customers/1/edit",
        data={
            "name": "Updated Customer",
            "customer_type": "INDIVIDUAL",
            "phone": "999",
            "email": "updated@example.com",
            "address": "Yei",
            "notes": "Updated",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/customers/1"
    )

    assert captured["customer"] is customer
    assert customer.name == "Updated Customer"
    assert customer.customer_type == "INDIVIDUAL"
    assert customer.phone == "999"
    assert customer.email == "updated@example.com"
    assert customer.address == "Yei"
    assert customer.notes == "Updated"


def test_activate_customer_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/customers/1/activate"
    )

    assert response.status_code == 403


def test_activate_customer_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    customer = SimpleNamespace(
        id=1,
        is_active=True,
    )

    captured = {}

    class FakeCustomerService:
        def activate(self, customer_id):
            captured["customer_id"] = customer_id
            return customer

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    response = authenticated_client.post(
        "/catering/customers/1/activate",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/customers/1"
    )

    assert captured["customer_id"] == 1


def test_deactivate_customer_requires_update_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/customers/1/deactivate"
    )

    assert response.status_code == 403


def test_deactivate_customer_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    customer = SimpleNamespace(
        id=1,
        is_active=False,
    )

    captured = {}

    class FakeCustomerService:
        def deactivate(self, customer_id):
            captured["customer_id"] = customer_id
            return customer

    monkeypatch.setattr(
        catering_routes,
        "CustomerService",
        FakeCustomerService,
    )

    response = authenticated_client.post(
        "/catering/customers/1/deactivate",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/customers/1"
    )

    assert captured["customer_id"] == 1
