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

from decimal import Decimal
from types import SimpleNamespace

from app.modules.procurement.integration.contracts import (
    InventoryReceiptStatusQueryResult,
)
from app.modules.procurement.integration.receipt_status import (
    FULLY_RECEIVED,
    STATUS_UNAVAILABLE,
    PurchaseOrderLineReceiptStatus,
)


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

    created = []

    class FakePurchaseOrderService:
        def create(self, entity):
            created.append(entity)
            return entity

    class FakeSupplier:
        def __init__(self, supplier_id, name):
            self.id = supplier_id
            self.name = name

    class FakeSupplierService:
        def paginate(self, options):
            class Result:
                items = [
                    FakeSupplier(1, "Supplier One"),
                ]

            return Result()

    class FakePurchaseRequest:
        def __init__(self, purchase_request_id, reference, status):
            self.id = purchase_request_id
            self.reference = reference
            self.status = status

    class FakePurchaseRequestService:
        def paginate(self, options):
            assert options.filters == {"status": "APPROVED"}

            class Result:
                items = [
                    FakePurchaseRequest(
                        7,
                        "PReq-007",
                        "APPROVED",
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

    valid_data = {
        "reference": "PO-001",
        "currency": "USD",
        "supplier_id": "1",
        "order_date": "2026-09-15",
        "expected_delivery_date": "2026-09-30",
        "status": "DRAFT",
        "purchase_request_id": "7",
    }

    response = authenticated_client.post(
        "/procurement/purchase-orders/create",
        data=valid_data,
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-orders/"
    )
    assert len(created) == 1

    entity = created[0]
    assert entity.reference == "PO-001"
    assert entity.currency == "USD"
    assert entity.supplier_id == 1
    assert entity.order_date == date(2026, 9, 15)
    assert entity.expected_delivery_date == date(2026, 9, 30)
    assert entity.status == "DRAFT"
    assert entity.purchase_request_id == 7

    # A request outside the approved choices must not be accepted.
    invalid_data = {
        **valid_data,
        "reference": "PO-INVALID-001",
        "currency": "USD",
        "purchase_request_id": "8",
    }

    response = authenticated_client.post(
        "/procurement/purchase-orders/create",
        data=invalid_data,
        follow_redirects=False,
    )

    assert response.status_code == 200
    assert len(created) == 1


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


def test_purchase_order_edit_rejects_non_draft_order(
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

    purchase_order = SimpleNamespace(
        id=1,
        status="APPROVED",
    )

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

        def update(self, entity):
            raise AssertionError(
                "A non-DRAFT Purchase Order must not be updated."
            )

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/1/edit",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-orders/1"
    )


def test_purchase_order_edit_rejects_direct_status_change(
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

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

        def update(self, entity):
            raise AssertionError(
                "Generic editing must not change Purchase Order status."
            )

    class FakeSupplier:
        def __init__(self, supplier_id, name):
            self.id = supplier_id
            self.name = name

    class FakeSupplierService:
        def paginate(self, options):
            class Result:
                items = [
                    FakeSupplier(3, "Supplier Three"),
                    FakeSupplier(4, "Supplier Four"),
                ]

            return Result()

    class FakePurchaseRequest:
        def __init__(self, purchase_request_id, reference, status):
            self.id = purchase_request_id
            self.reference = reference
            self.status = status

    class FakePurchaseRequestService:
        def paginate(self, options):
            assert options.filters == {"status": "APPROVED"}

            class Result:
                items = [
                    FakePurchaseRequest(
                        8,
                        "PReq-008",
                        "APPROVED",
                    ),
                ]

            return Result()

        def get(self, purchase_request_id):
            if purchase_request_id == 7:
                return FakePurchaseRequest(
                    7,
                    "PReq-007",
                    "REJECTED",
                )
            return None

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
            "currency": "USD",
            "supplier_id": "4",
            "order_date": "2026-09-20",
            "expected_delivery_date": "2026-10-15",
            "status": "SUBMITTED",
            "purchase_request_id": "8",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-orders/1"
    )
    assert purchase_order.status == "DRAFT"


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
        def __init__(self, supplier_id, name):
            self.id = supplier_id
            self.name = name

    class FakeSupplierService:
        def paginate(self, options):
            class Result:
                items = [
                    FakeSupplier(3, "Supplier Three"),
                    FakeSupplier(4, "Supplier Four"),
                ]

            return Result()

    class FakePurchaseRequest:
        def __init__(self, purchase_request_id, reference, status):
            self.id = purchase_request_id
            self.reference = reference
            self.status = status

    class FakePurchaseRequestService:
        def paginate(self, options):
            assert options.filters == {"status": "APPROVED"}

            class Result:
                items = [
                    FakePurchaseRequest(
                        8,
                        "PReq-008",
                        "APPROVED",
                    ),
                ]

            return Result()

        def get(self, purchase_request_id):
            if purchase_request_id == 7:
                return FakePurchaseRequest(
                    7,
                    "PReq-007",
                    "REJECTED",
                )
            return None

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
            "currency": "USD",
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


def test_purchase_order_delete_rejects_non_draft_order(
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

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 7
            return SimpleNamespace(
                id=7,
                status="APPROVED",
            )

        def delete(self, purchase_order_id):
            raise AssertionError(
                "A non-DRAFT Purchase Order must not be deleted."
            )

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
        "/procurement/purchase-orders/7"
    )


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
        def get(self, purchase_order_id):
            assert purchase_order_id == 7
            return SimpleNamespace(
                id=7,
                status="DRAFT",
            )

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


def test_purchase_order_view_derives_receipt_status_for_mapped_line(
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

    line = SimpleNamespace(
        id=7,
        guid="test-line-guid-001",
        description="Bottled Water",
        quantity=Decimal("12"),
        unit="bottle",
        stock_item_reference="UAT-WATER-001",
    )
    purchase_order = SimpleNamespace(
        id=1,
        reference="PO-VIEW-STATUS-001",
        lines=[line],
    )

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

    def fake_query(query_request):
        assert query_request.purchase_order_reference == (
            "PO-VIEW-STATUS-001"
        )
        assert query_request.purchase_order_line_reference == (
            "PO-LINE-test-line-guid-001"
        )
        assert query_request.stock_item_reference == "UAT-WATER-001"

        return InventoryReceiptStatusQueryResult(
            success=True,
            purchase_order_reference="PO-VIEW-STATUS-001",
            purchase_order_line_reference=(
                "PO-LINE-test-line-guid-001"
            ),
            received_quantity=Decimal("12"),
            unit="bottle",
            receipt_count=1,
            has_receipts=True,
        )

    captured = {}

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes."
        "InventoryReceiptStatusQueryProvider.query",
        fake_query,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/1",
    )

    assert response.status_code == 200
    assert captured["context"]["purchase_order"] is purchase_order
    assert (
        captured["context"]["receipt_statuses"][7].status
        == FULLY_RECEIVED
    )


def test_purchase_order_view_marks_unmapped_line_status_unavailable(
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

    line = SimpleNamespace(
        id=8,
        guid="test-line-guid-002",
        description="Unmapped Item",
        quantity=Decimal("3"),
        unit="box",
        stock_item_reference=None,
    )
    purchase_order = SimpleNamespace(
        id=2,
        reference="PO-VIEW-STATUS-002",
        lines=[line],
    )

    class FakePurchaseOrderService:
        def get(self, purchase_order_id):
            assert purchase_order_id == 2
            return purchase_order

    def unexpected_query(_query_request):
        raise AssertionError(
            "Inventory must not be queried without an explicit mapping."
        )

    captured = {}

    def fake_render_template(template, **context):
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseOrderService",
        FakePurchaseOrderService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes."
        "InventoryReceiptStatusQueryProvider.query",
        unexpected_query,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-orders/2",
    )

    assert response.status_code == 200
    assert (
        captured["context"]["receipt_statuses"][8].status
        == STATUS_UNAVAILABLE
    )
