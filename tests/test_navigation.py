from app.navigation.menu import MENU_ITEMS
from app.security.authorization import AuthorizationService


INVENTORY_PERMISSIONS = {
    "catering.stock_item.read": "Stock Items",
    "catering.inventory_location.read": "Inventory Locations",
    "catering.stock_balance.read": "Stock Balances",
    "catering.stock_movement.read": "Stock Movements",
    "catering.stock_transfer.read": "Stock Transfers",
}


def build_template_context(app):
    """Build the real Flask template context for a request."""
    with app.test_request_context("/"):
        context = {}
        app.update_template_context(context)
        return context


def find_inventory_group(menu_items):
    return next(
        (
            item
            for item in menu_items
            if item["title"] == "Inventory Management"
        ),
        None,
    )


def test_inventory_management_shows_only_permitted_links(app, monkeypatch):
    allowed_permissions = {
        "catering.stock_item.read",
        "catering.stock_movement.read",
    }
    monkeypatch.setattr(
        AuthorizationService,
        "has_permission",
        staticmethod(lambda permission: permission in allowed_permissions),
    )

    context = build_template_context(app)
    group = find_inventory_group(context["menu_items"])

    assert group is not None
    assert [child["title"] for child in group["children"]] == [
        "Stock Items",
        "Stock Movements",
    ]
    assert all("permission" not in child for child in group["children"])
    assert "hide_if_empty" not in group


def test_inventory_management_is_hidden_without_inventory_permissions(
    app,
    monkeypatch,
):
    monkeypatch.setattr(
        AuthorizationService,
        "has_permission",
        staticmethod(lambda permission: False),
    )

    context = build_template_context(app)

    assert find_inventory_group(context["menu_items"]) is None


def test_inventory_management_exposes_all_five_links_when_permitted(
    app,
    monkeypatch,
):
    monkeypatch.setattr(
        AuthorizationService,
        "has_permission",
        staticmethod(lambda permission: permission in INVENTORY_PERMISSIONS),
    )

    context = build_template_context(app)
    group = find_inventory_group(context["menu_items"])

    assert group is not None
    assert {
        child["title"]: child["endpoint"]
        for child in group["children"]
    } == {
        "Stock Items": "catering.stock_items",
        "Inventory Locations": "catering.locations",
        "Stock Balances": "catering.balances",
        "Stock Movements": "catering.movements",
        "Stock Transfers": "catering.transfers",
    }


def test_navigation_preserves_existing_menu_and_brand_context(
    app,
    monkeypatch,
):
    monkeypatch.setattr(
        AuthorizationService,
        "has_permission",
        staticmethod(lambda permission: False),
    )

    context = build_template_context(app)
    expected_titles = {
        item["title"]
        for item in MENU_ITEMS
        if item["title"] != "Inventory Management"
    }
    actual_titles = {
        item["title"]
        for item in context["menu_items"]
    }

    assert expected_titles <= actual_titles
    assert context.get("brand")
