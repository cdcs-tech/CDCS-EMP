"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory Stock Balance route tests.
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


def test_balances_requires_authentication(client):
    response = client.get(
        "/catering/balances/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_balances_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/balances/"
    )

    assert response.status_code == 403


def test_balances_list_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = SimpleNamespace(
        items=["balance-1"],
    )

    captured = {}

    class FakeStockBalanceService:
        def paginate(self, options):
            assert options.page == 1
            assert options.page_size == 25
            assert options.sort_by == "stock_item_id"
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
        "StockBalanceService",
        FakeStockBalanceService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/balances/"
    )

    assert response.status_code == 200
    assert response.text == "rendered"

    assert captured["template"] == (
        "modules/catering/balances/index.html"
    )

    assert captured["context"]["balances"] == [
        "balance-1"
    ]

    assert captured["context"]["pagination"] is result


def test_balances_supports_controlled_query_options(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeStockBalanceService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    def fake_render_template(template, **context):
        return "rendered"

    monkeypatch.setattr(
        catering_routes,
        "StockBalanceService",
        FakeStockBalanceService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/balances/"
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


def test_balances_rejects_unsupported_sort_field(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    captured = {}

    class FakeStockBalanceService:
        def paginate(self, options):
            captured["options"] = options

            return SimpleNamespace(
                items=[],
            )

    monkeypatch.setattr(
        catering_routes,
        "StockBalanceService",
        FakeStockBalanceService,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        lambda template, **context: "rendered",
    )

    response = authenticated_client.get(
        "/catering/balances/"
        "?sort=invalid_field"
    )

    assert response.status_code == 200

    assert captured["options"].sort_by == (
        "stock_item_id"
    )
