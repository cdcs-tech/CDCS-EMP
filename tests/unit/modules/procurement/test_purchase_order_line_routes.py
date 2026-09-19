"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase order line route tests.
"""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

from app.models.role_permission import RolePermission
from tests.factories.permission_factory import PermissionFactory


def _grant_permission(
    session,
    admin_user,
    permission_name: str,
):
    """
    Grant a permission to the Administrator role used by
    the authenticated test user.
    """
    role = admin_user.user_roles[0].role

    permission = PermissionFactory.create(
        session=session,
        name=permission_name,
        module="PROCUREMENT",
        description=(
            f"Test permission: {permission_name}"
        ),
        commit=False,
    )

    session.add(
        RolePermission(
            role=role,
            permission=permission,
        )
    )

    session.commit()

    return permission


def test_create_purchase_order_line_requires_login(
    client,
):
    response = client.get(
        "/procurement/purchase-orders/1/lines/create",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_create_purchase_order_line_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-orders/1/lines/create",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_create_purchase_order_line_renders_form(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order_line.create",
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-001",
    )

    class FakePurchaseOrderService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_order

    captured = {}

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/1/lines/create"
    )

    assert response.status_code == 200

    assert captured["template"] == (
        "modules/procurement/purchase_orders/line_form.html"
    )

    assert (
        captured["context"]["purchase_order"]
        is purchase_order
    )

    assert captured["context"]["page_title"] == (
        "Add Purchase Order Line"
    )


def test_create_purchase_order_line_creates_line(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order_line.create",
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-001",
    )

    created = {}

    class FakePurchaseOrderService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_order

    class FakePurchaseOrderLineService:
        def create(self, line):
            created["line"] = line
            return line

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        routes,
        "PurchaseOrderLineService",
        FakePurchaseOrderLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/lines/create",
        data={
            "description": "Bottled Water",
            "item_reference": "WATER-001",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "170.00",
            "notes": "For office use.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert "/procurement/purchase-orders/1" in (
        response.headers["Location"]
    )

    line = created["line"]

    assert line.purchase_order_id == 1
    assert line.description == "Bottled Water"
    assert line.item_reference == "WATER-001"
    assert line.quantity == Decimal("20.000")
    assert line.unit == "Carton"
    assert line.unit_price == Decimal("8.50")
    assert line.total_amount == Decimal("170.00")
    assert line.notes == "For office use."


def test_edit_purchase_order_line_requires_login(
    client,
):
    response = client.get(
        "/procurement/purchase-orders/1/lines/2/edit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_edit_purchase_order_line_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-orders/1/lines/2/edit",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_edit_purchase_order_line_rejects_wrong_parent(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order_line.update",
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_order_id=99,
    )

    class FakePurchaseOrderService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_order

    class FakePurchaseOrderLineService:
        def get(self, entity_id):
            assert entity_id == 2
            return line

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        routes,
        "PurchaseOrderLineService",
        FakePurchaseOrderLineService,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/1/lines/2/edit"
    )

    assert response.status_code == 404


def test_edit_purchase_order_line_updates_line(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order_line.update",
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_order_id=1,
        description="Old Description",
        item_reference="OLD-001",
        quantity=Decimal("5.000"),
        unit="Box",
        unit_price=Decimal("10.00"),
        total_amount=Decimal("50.00"),
        notes="Old notes.",
    )

    updated = {}

    class FakePurchaseOrderService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_order

    class FakePurchaseOrderLineService:
        def get(self, entity_id):
            assert entity_id == 2
            return line

        def update(self, entity):
            updated["line"] = entity
            return entity

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        routes,
        "PurchaseOrderLineService",
        FakePurchaseOrderLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/lines/2/edit",
        data={
            "description": "Updated Bottled Water",
            "item_reference": "WATER-002",
            "quantity": "25.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "212.50",
            "notes": "Updated quantity.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert "/procurement/purchase-orders/1" in (
        response.headers["Location"]
    )

    assert updated["line"] is line

    assert line.purchase_order_id == 1
    assert line.description == "Updated Bottled Water"
    assert line.item_reference == "WATER-002"
    assert line.quantity == Decimal("25.000")
    assert line.unit == "Carton"
    assert line.unit_price == Decimal("8.50")
    assert line.total_amount == Decimal("212.50")
    assert line.notes == "Updated quantity."


def test_delete_purchase_order_line_requires_login(
    client,
):
    response = client.post(
        "/procurement/purchase-orders/1/lines/2/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_delete_purchase_order_line_requires_permission(
    authenticated_client,
):
    response = authenticated_client.post(
        "/procurement/purchase-orders/1/lines/2/delete",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_delete_purchase_order_line_rejects_wrong_parent(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order_line.delete",
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_order_id=99,
    )

    class FakePurchaseOrderService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_order

    class FakePurchaseOrderLineService:
        def get(self, entity_id):
            assert entity_id == 2
            return line

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        routes,
        "PurchaseOrderLineService",
        FakePurchaseOrderLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/lines/2/delete",
        follow_redirects=False,
    )

    assert response.status_code == 404


def test_delete_purchase_order_line_deletes_line(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order_line.delete",
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_order_id=1,
    )

    deleted = {}

    class FakePurchaseOrderService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_order

    class FakePurchaseOrderLineService:
        def get(self, entity_id):
            assert entity_id == 2
            return line

        def delete(self, entity_id):
            deleted["id"] = entity_id

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        routes,
        "PurchaseOrderLineService",
        FakePurchaseOrderLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/lines/2/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert "/procurement/purchase-orders/1" in (
        response.headers["Location"]
    )

    assert deleted["id"] == 2
