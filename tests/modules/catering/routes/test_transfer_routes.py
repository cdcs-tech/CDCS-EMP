"""
OW-1.4.4 — Stock Transfer route tests.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models.user import User

import app.modules.catering.routes.routes as catering_routes

from app.core.crud.exceptions import EntityNotFoundException


class FakeModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeRepository:
    model = FakeModel


class FakePaginatedResult:
    def __init__(self, items):
        self.items = items


def _allow_permissions(monkeypatch):
    """
    Explicitly authorize successful route-path tests.
    """

    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: True,
    )


def test_transfers_requires_authentication(client):
    response = client.get(
        "/catering/transfers/"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_transfers_requires_read_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/transfers/"
    )

    assert response.status_code == 403


def test_transfers_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    result = FakePaginatedResult(
        [
            SimpleNamespace(
                id=1,
                reference="TR-001",
            )
        ]
    )

    service = MagicMock()
    service.paginate.return_value = result

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        lambda: service,
    )

    captured = {}

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "ok"

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/transfers/"
    )

    assert response.status_code == 200

    service.paginate.assert_called_once()

    options = service.paginate.call_args.args[0]

    assert options.page == 1
    assert options.page_size == 25
    assert options.sort_by == "occurred_at"
    assert options.sort_direction == "asc"

    assert (
        captured["template"]
        == "modules/catering/transfers/index.html"
    )

    assert (
        captured["context"]["transfers"]
        == result.items
    )

    assert (
        captured["context"]["pagination"]
        is result
    )


def test_transfers_builds_controlled_query_options(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    service = MagicMock()

    service.paginate.return_value = FakePaginatedResult(
        []
    )

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        lambda: service,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        lambda template, **context: "ok",
    )

    response = authenticated_client.get(
        "/catering/transfers/"
        "?page=2"
        "&page_size=50"
        "&sort=reference"
        "&direction=desc"
        "&search=TR-001"
    )

    assert response.status_code == 200

    options = service.paginate.call_args.args[0]

    assert options.page == 2
    assert options.page_size == 50
    assert options.sort_by == "reference"
    assert options.sort_direction == "desc"
    assert options.search == "TR-001"


def test_transfers_invalid_sort_falls_back_to_occurred_at(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    service = MagicMock()

    service.paginate.return_value = FakePaginatedResult(
        []
    )

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        lambda: service,
    )

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        lambda template, **context: "ok",
    )

    response = authenticated_client.get(
        "/catering/transfers/"
        "?sort=invalid"
    )

    assert response.status_code == 200

    options = service.paginate.call_args.args[0]

    assert options.sort_by == "occurred_at"


def test_create_transfer_requires_create_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.get(
        "/catering/transfers/create"
    )

    assert response.status_code == 403


def test_create_transfer_populates_active_choices(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    stock_item = SimpleNamespace(
        id=1,
        is_active=True,
        product=SimpleNamespace(
            name="Rice"
        ),
    )

    inactive_stock_item = SimpleNamespace(
        id=2,
        is_active=False,
        product=SimpleNamespace(
            name="Inactive Rice"
        ),
    )

    location = SimpleNamespace(
        id=10,
        name="Main Store",
        is_active=True,
    )

    inactive_location = SimpleNamespace(
        id=11,
        name="Closed Store",
        is_active=False,
    )

    stock_item_service = MagicMock()
    stock_item_service.get_all.return_value = [
        stock_item,
        inactive_stock_item,
    ]

    location_service = MagicMock()
    location_service.get_all.return_value = [
        location,
        inactive_location,
    ]

    monkeypatch.setattr(
        catering_routes,
        "StockItemService",
        lambda: stock_item_service,
    )

    monkeypatch.setattr(
        catering_routes,
        "InventoryLocationService",
        lambda: location_service,
    )

    captured = {}

    def fake_render_template(
        template,
        **context,
    ):
        captured["form"] = context["form"]
        return "ok"

    monkeypatch.setattr(
        catering_routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/catering/transfers/create"
    )

    assert response.status_code == 200

    form = captured["form"]

    assert form.stock_item_id.choices == [
        (1, "Rice")
    ]

    assert form.source_location_id.choices == [
        (10, "Main Store")
    ]

    assert form.destination_location_id.choices == [
        (10, "Main Store")
    ]


def test_create_transfer_delegates_draft_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    stock_item = SimpleNamespace(
        id=1,
        is_active=True,
        product=SimpleNamespace(
            name="Rice"
        ),
    )

    source_location = SimpleNamespace(
        id=10,
        name="Main Store",
        is_active=True,
    )

    destination_location = SimpleNamespace(
        id=20,
        name="Kitchen Store",
        is_active=True,
    )

    stock_item_service = MagicMock()
    stock_item_service.get_all.return_value = [
        stock_item
    ]

    location_service = MagicMock()
    location_service.get_all.return_value = [
        source_location,
        destination_location,
    ]

    monkeypatch.setattr(
        catering_routes,
        "StockItemService",
        lambda: stock_item_service,
    )

    monkeypatch.setattr(
        catering_routes,
        "InventoryLocationService",
        lambda: location_service,
    )

    service = MagicMock()
    service.repository = FakeRepository()
    service.create.return_value = FakeModel(
        id=1
    )

    captured = {}

    def fake_stock_transfer_service(
        **kwargs,
    ):
        captured["service_kwargs"] = kwargs
        return service

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        fake_stock_transfer_service,
    )

    response = authenticated_client.post(
        "/catering/transfers/create",
        data={
            "stock_item_id": "1",
            "source_location_id": "10",
            "destination_location_id": "20",
            "quantity": "5.000",
            "reference": "TR-001",
            "reason": "Move stock",
            "occurred_at": "2026-08-31T10:00",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert (
        captured["service_kwargs"]["authorization_adapter"]
        is not None
    )

    service.create.assert_called_once()

    created_transfer = service.create.call_args.args[0]
    create_kwargs = service.create.call_args.kwargs

    assert created_transfer.stock_item_id == 1
    assert created_transfer.source_location_id == 10
    assert created_transfer.destination_location_id == 20
    assert str(created_transfer.quantity) == "5.000"
    assert created_transfer.reference == "TR-001"
    assert created_transfer.reason == "Move stock"
    assert created_transfer.status == "DRAFT"

    assert (
        create_kwargs["subject"]
        is catering_routes.current_user
    )


def test_post_transfer_requires_post_permission(
    authenticated_client,
    monkeypatch,
):
    monkeypatch.setattr(
        User,
        "has_permission",
        lambda self, permission: False,
    )

    response = authenticated_client.post(
        "/catering/transfers/1/post"
    )

    assert response.status_code == 403


def test_post_transfer_delegates_to_service(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    transfer = SimpleNamespace(
        id=1,
        status="DRAFT",
    )

    service = MagicMock()
    service.get.return_value = transfer

    captured = {}

    def fake_stock_transfer_service(
        **kwargs,
    ):
        captured["service_kwargs"] = kwargs
        return service

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        fake_stock_transfer_service,
    )

    response = authenticated_client.post(
        "/catering/transfers/1/post"
    )

    assert response.status_code == 302

    service.get.assert_called_once_with(
        1
    )

    service.post_transfer.assert_called_once_with(
        transfer,
        subject=catering_routes.current_user,
    )

    assert (
        captured["service_kwargs"]["authorization_adapter"]
        is not None
    )


def test_post_transfer_handles_missing_transfer(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    service = MagicMock()

    service.get.side_effect = EntityNotFoundException(
        "StockTransfer",
        999,
    )

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        lambda **kwargs: service,
    )

    response = authenticated_client.post(
        "/catering/transfers/999/post"
    )

    assert response.status_code == 302

    service.get.assert_called_once_with(
        999
    )

    service.post_transfer.assert_not_called()


def test_post_transfer_handles_service_error(
    authenticated_client,
    monkeypatch,
):
    _allow_permissions(monkeypatch)

    transfer = SimpleNamespace(
        id=1,
        status="DRAFT",
    )

    service = MagicMock()

    service.get.return_value = transfer

    service.post_transfer.side_effect = ValueError(
        "Insufficient stock for transfer."
    )

    monkeypatch.setattr(
        catering_routes,
        "StockTransferService",
        lambda **kwargs: service,
    )

    response = authenticated_client.post(
        "/catering/transfers/1/post"
    )

    assert response.status_code == 302

    service.get.assert_called_once_with(
        1
    )

    service.post_transfer.assert_called_once_with(
        transfer,
        subject=catering_routes.current_user,
    )
