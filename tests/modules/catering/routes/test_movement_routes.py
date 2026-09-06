"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory Stock Movement route tests.
"""

from datetime import datetime
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


def test_movements_requires_authentication(client):
    response = client.get(
        "/catering/movements/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_movements_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/movements/"
    )

    assert response.status_code == 403


def test_movements_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["movement-1"],
    )

    captured = {}

    class FakeStockMovementService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            assert options.sort_by == "occurred_at"
            assert options.sort_direction == "asc"
            assert options.search is None
            assert options.filters == {}
            return result

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "StockMovementService",
        FakeStockMovementService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/movements/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/movements/index.html"
    )

    assert captured["context"]["movements"] == [
        "movement-1"
    ]

    assert captured["context"]["pagination"] is result


def test_movements_supports_controlled_query_options(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeStockMovementService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        catering_routes,
        "StockMovementService",
        FakeStockMovementService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/catering/movements/"
        "?page=2"
        "&page_size=50"
        "&sort=quantity"
        "&direction=desc"
        "&search=rice"
    )

    assert response.status_code == 200

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 50
    assert options.sort_by == "quantity"
    assert options.sort_direction == "desc"
    assert options.search == "rice"
    assert options.filters == {}


def test_create_movement_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/movements/create"
    )

    assert response.status_code == 403


def test_create_movement_populates_active_choices(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    stock_items = [
        SimpleNamespace(
            id=1,
            is_active=True,
            product=SimpleNamespace(name="Rice"),
        ),
        SimpleNamespace(
            id=2,
            is_active=False,
            product=SimpleNamespace(name="Beans"),
        ),
    ]

    locations = [
        SimpleNamespace(
            id=10,
            name="Main Store",
            is_active=True,
        ),
        SimpleNamespace(
            id=11,
            name="Closed Store",
            is_active=False,
        ),
    ]

    captured = {}

    class FakeStockItemService:
        def get_all(self):
            return stock_items

    class FakeLocationService:
        def get_all(self):
            return locations

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
        "InventoryLocationService",
        FakeLocationService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/movements/create"
    )

    assert response.status_code == 200

    form = captured["context"]["form"]

    assert form.stock_item_id.choices == [
        (1, "Rice"),
    ]

    assert form.location_id.choices == [
        (10, "Main Store"),
    ]


def test_create_movement_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    stock_items = [
        SimpleNamespace(
            id=1,
            is_active=True,
            product=SimpleNamespace(name="Rice"),
        ),
    ]

    locations = [
        SimpleNamespace(
            id=10,
            name="Main Store",
            is_active=True,
        ),
    ]

    class FakeStockItemService:
        def get_all(self):
            return stock_items

    class FakeLocationService:
        def get_all(self):
            return locations

    created = {}

    class FakeModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class FakeRepository:
        model = FakeModel

    class FakeStockMovementService:
        repository = FakeRepository()

        def __init__(self, authorization_adapter=None):
            created["adapter"] = authorization_adapter

        def create(self, entity, *, subject):
            created["entity"] = entity
            created["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "StockItemService",
        FakeStockItemService,
    )

    monkeypatch.setattr(
        catering_routes,
        "InventoryLocationService",
        FakeLocationService,
    )

    monkeypatch.setattr(
        catering_routes,
        "StockMovementService",
        FakeStockMovementService,
    )

    response = authenticated_client.post(
        "/catering/movements/create",
        data={
            "stock_item_id": "1",
            "location_id": "10",
            "movement_type": "RECEIPT",
            "quantity": "25",
            "reference": "GRN-001",
            "reason": "Initial receipt",
            "occurred_at": "2026-09-07T10:00",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/movements/"
    )

    entity = created["entity"]

    assert entity.stock_item_id == 1
    assert entity.location_id == 10
    assert entity.movement_type == "RECEIPT"
    assert entity.quantity == 25
    assert entity.reference == "GRN-001"
    assert entity.reason == "Initial receipt"

    assert created["subject"] is not None
    assert created["adapter"] is not None


def test_post_movement_requires_post_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/movements/1/post"
    )

    assert response.status_code == 403


def test_post_movement_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    movement = SimpleNamespace(
        id=1,
        status="DRAFT",
    )

    captured = {}

    class FakeStockMovementService:
        def __init__(self, authorization_adapter=None):
            captured["adapter"] = authorization_adapter

        def get(self, movement_id):
            assert movement_id == 1
            return movement

        def post_movement(self, entity, *, subject):
            captured["movement"] = entity
            captured["subject"] = subject
            return entity

    monkeypatch.setattr(
        catering_routes,
        "StockMovementService",
        FakeStockMovementService,
    )

    response = authenticated_client.post(
        "/catering/movements/1/post",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/catering/movements/"
    )

    assert captured["movement"] is movement
    assert captured["subject"] is not None
    assert captured["adapter"] is not None
