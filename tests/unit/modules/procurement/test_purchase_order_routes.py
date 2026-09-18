"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase order route tests.
"""

from __future__ import annotations

from datetime import date

from app.modules.procurement.models import PurchaseOrder
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


def test_purchase_order_list_requires_login(
    client,
):
    response = client.get(
        "/procurement/purchase-orders/",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_purchase_order_list_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-orders/",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_order_list_route_is_registered(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.read",
    )

    captured = {}

    class FakePurchaseOrderService:
        def paginate(self, options):
            captured["options"] = options
            return "result"

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/"
        "?search=PO"
        "&status=DRAFT"
        "&sort=reference"
        "&direction=desc"
        "&page=2"
        "&page_size=10"
    )

    assert response.status_code == 200

    assert captured["template"] == (
        "modules/procurement/purchase_orders/index.html"
    )

    assert captured["context"]["purchase_orders"] == "result"

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 10
    assert options.sort_by == "reference"
    assert options.sort_direction == "desc"
    assert options.search == "PO"
    assert options.filters == {"status": "DRAFT"}


def test_purchase_order_create_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-orders/create",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_order_create_submits_valid_order(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.create",
    )

    created = {}

    class FakePurchaseOrderService:
        def create(self, entity):
            created["entity"] = entity
            return entity

    class FakeSupplier:
        def __init__(
            self,
            supplier_id,
            name,
        ):
            self.id = supplier_id
            self.name = name

    class FakeSupplierService:
        def paginate(self, options):
            class Result:
                items = [
                    FakeSupplier(
                        1,
                        "Supplier One",
                    ),
                ]

            return Result()

    class FakePurchaseRequest:
        def __init__(
            self,
            purchase_request_id,
            reference,
        ):
            self.id = purchase_request_id
            self.reference = reference

    class FakePurchaseRequestService:
        def paginate(self, options):
            class Result:
                items = [
                    FakePurchaseRequest(
                        7,
                        "PReq-007",
                    ),
                ]

            return Result()

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/create",
        data={
            "reference": "PO-001",
            "supplier_id": "1",
            "order_date": "2026-09-15",
            "expected_delivery_date": "2026-09-30",
            "status": "DRAFT",
            "purchase_request_id": "7",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert response.headers["Location"].endswith(
        "/procurement/purchase-orders/"
    )

    entity = created["entity"]

    assert entity.reference == "PO-001"
    assert entity.supplier_id == 1
    assert entity.order_date == date(2026, 9, 15)
    assert entity.expected_delivery_date == date(2026, 9, 30)
    assert entity.status == "DRAFT"
    assert entity.purchase_request_id == 7


def test_purchase_order_view_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-orders/1",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_order_view_renders_for_authorized_user(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.read",
    )

    purchase_order = PurchaseOrder(
        id=1,
        reference="PO-VIEW-001",
        supplier_id=3,
        order_date=date(2026, 9, 15),
        expected_delivery_date=date(2026, 9, 30),
        status="DRAFT",
        purchase_request_id=7,
    )

    captured = {}

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/1",
    )

    assert response.status_code == 200

    assert captured["template"] == (
        "modules/procurement/purchase_orders/view.html"
    )

    assert (
        captured["context"]["purchase_order"]
        is purchase_order
    )


def test_purchase_order_edit_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-orders/1/edit",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_order_edit_submits_updated_order(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.update",
    )

    purchase_order = PurchaseOrder(
        id=1,
        reference="PO-EDIT-001",
        supplier_id=3,
        order_date=date(2026, 9, 15),
        expected_delivery_date=date(2026, 9, 30),
        status="DRAFT",
        purchase_request_id=7,
    )

    updated = {}

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

        def update(self, entity):
            updated["entity"] = entity
            return entity

    class FakeSupplier:
        def __init__(
            self,
            supplier_id,
            name,
        ):
            self.id = supplier_id
            self.name = name

    class FakeSupplierService:
        def paginate(self, options):
            class Result:
                items = [
                    FakeSupplier(
                        3,
                        "Supplier Three",
                    ),
                    FakeSupplier(
                        4,
                        "Supplier Four",
                    ),
                ]

            return Result()

    class FakePurchaseRequest:
        def __init__(
            self,
            purchase_request_id,
            reference,
        ):
            self.id = purchase_request_id
            self.reference = reference

    class FakePurchaseRequestService:
        def paginate(self, options):
            class Result:
                items = [
                    FakePurchaseRequest(
                        7,
                        "PReq-007",
                    ),
                    FakePurchaseRequest(
                        8,
                        "PReq-008",
                    ),
                ]

            return Result()

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/edit",
        data={
            "reference": "PO-EDIT-002",
            "supplier_id": "4",
            "order_date": "2026-09-20",
            "expected_delivery_date": "2026-10-15",
            "status": "DRAFT",
            "purchase_request_id": "8",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert response.headers["Location"].endswith(
        "/procurement/purchase-orders/1"
    )

    entity = updated["entity"]

    assert entity.reference == "PO-EDIT-002"
    assert entity.supplier_id == 4
    assert entity.order_date == date(2026, 9, 20)
    assert entity.expected_delivery_date == date(2026, 10, 15)
    assert entity.status == "DRAFT"
    assert entity.purchase_request_id == 8


def test_purchase_order_delete_requires_permission(
    authenticated_client,
):
    response = authenticated_client.post(
        "/procurement/purchase-orders/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_order_delete_submits_delete(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.delete",
    )

    deleted = {}

    class FakePurchaseOrderService:
        def delete(self, purchase_order_id):
            deleted["id"] = purchase_order_id

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/7/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert response.headers["Location"].endswith(
        "/procurement/purchase-orders/"
    )

    assert deleted["id"] == 7
