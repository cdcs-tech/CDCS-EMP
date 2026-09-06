"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory Stock Item and Location route tests.
"""

from types import SimpleNamespace

from app.models.user import User

import app.modules.catering.routes.routes as catering_routes


def _allow_permissions(monkeypatch):
    """
    Explicitly authorize successful route-path tests.

    Dedicated authorization tests separately verify that missing
    permissions are rejected with HTTP 403.
    """
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def test_stock_items_requires_authentication(client):
    response = client.get("/catering/stock-items/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_stock_items_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/stock-items/"
    )

    assert response.status_code == 403


def test_stock_items_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["stock-item-1"],
    )

    captured = {}

    class FakeStockItemService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            return result

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "StockItemService",
        FakeStockItemService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/stock-items/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/stock_items/index.html"
    )
    assert captured["context"]["stock_items"] == [
        "stock-item-1"
    ]
    assert captured["context"]["pagination"] is result


def test_create_stock_item_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/stock-items/create"
    )

    assert response.status_code == 403


def test_create_stock_item_populates_active_products(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    products = [
        SimpleNamespace(
            id=1,
            name="Rice",
            is_active=True,
        ),
        SimpleNamespace(
            id=2,
            name="Inactive Product",
            is_active=False,
        ),
    ]

    captured = {}

    class FakeProductService:
        def get_all(self):
            return products

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "ProductService",
        FakeProductService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/stock-items/create"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/stock_items/create.html"
    )

    form = captured["context"]["form"]

    assert form.product_id.choices == [
        (1, "Rice"),
    ]


def test_create_stock_item_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    products = [
        SimpleNamespace(
            id=1,
            name="Rice",
            is_active=True,
        ),
    ]

    class FakeProductService:
        def get_all(self):
            return products

    created = {}

    class FakeModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class FakeRepository:
        model = FakeModel

    class FakeStockItemService:
        repository = FakeRepository()

        def create(self, entity):
            created["entity"] = entity
            return entity

    monkeypatch.setattr(
        catering_routes,
        "ProductService",
        FakeProductService,
    )

    monkeypatch.setattr(
        catering_routes,
        "StockItemService",
        FakeStockItemService,
    )

    response = authenticated_client.post(
        "/catering/stock-items/create",
        data={
            "product_id": "1",
            "minimum_level": "10",
            "reorder_level": "20",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/stock-items/"
    )

    entity = created["entity"]

    assert entity.product_id == 1
    assert entity.minimum_level == 10
    assert entity.reorder_level == 20
    assert entity.is_active is True


def test_locations_requires_authentication(client):
    response = client.get("/catering/locations/")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_locations_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/locations/"
    )

    assert response.status_code == 403


def test_locations_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["location-1"],
    )

    captured = {}

    class FakeLocationService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            return result

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "InventoryLocationService",
        FakeLocationService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/locations/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/locations/index.html"
    )
    assert captured["context"]["locations"] == [
        "location-1"
    ]
    assert captured["context"]["pagination"] is result


def test_create_location_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/locations/create"
    )

    assert response.status_code == 403


def test_create_location_renders_form(
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
        "/catering/locations/create"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/locations/create.html"
    )
    assert "form" in captured["context"]


def test_create_location_delegates_to_service(
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

    class FakeLocationService:
        repository = FakeRepository()

        def create(self, entity):
            created["entity"] = entity
            return entity

    monkeypatch.setattr(
        catering_routes,
        "InventoryLocationService",
        FakeLocationService,
    )

    response = authenticated_client.post(
        "/catering/locations/create",
        data={
            "code": "MAIN",
            "name": "Main Store",
            "description": "Main catering store",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/locations/"
    )

    entity = created["entity"]

    assert entity.code == "MAIN"
    assert entity.name == "Main Store"
    assert entity.description == "Main catering store"
    assert entity.is_active is True
