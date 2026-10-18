"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase Order receiving route tests.
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
    """Grant the receiving permission to the test Administrator role."""
    role = admin_user.user_roles[0].role

    permission = PermissionFactory.create(
        session=session,
        name=permission_name,
        module="PROCUREMENT",
        description=f"Test permission: {permission_name}",
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


def _purchase_order(*, stock_item_reference: str | None):
    """Build an isolated approved Purchase Order with one line."""
    line = SimpleNamespace(
        id=7,
        guid="test-line-guid-001",
        description="Bottled Water",
        quantity=Decimal("10.000"),
        unit="Carton",
        stock_item_reference=stock_item_reference,
    )

    purchase_order = SimpleNamespace(
        id=1,
        reference="UAT-PO-ROUTE-001",
        status="APPROVED",
        lines=[line],
    )

    return purchase_order, line


def _receiving_form_data():
    """Return valid form data for a receiving-route POST."""
    return {
        "purchase_order_line_id": "7",
        "inventory_location_reference": "MAIN",
        "quantity_received": "5.000",
        "received_at": "2026-10-17T10:00",
        "receiving_reference": "UAT-GRN-ROUTE-001",
        "notes": "Isolated route test.",
    }


def test_receive_purchase_order_dispatches_distinct_references(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    """Dispatch must distinguish the PO line reference from Product code."""
    from app.modules.procurement.routes import routes

    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.receive",
    )

    purchase_order, line = _purchase_order(
        stock_item_reference="WATER-500ML",
    )

    class FakePurchaseOrderService:
        def get_by_id(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

    class FakeCommandDispatcher:
        def __init__(self):
            self.calls = []

        def dispatch(self, command, context):
            self.calls.append((command, context))
            return SimpleNamespace(
                success=True,
                message="Receipt submitted.",
            )

    dispatcher = FakeCommandDispatcher()

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )
    monkeypatch.setitem(
        authenticated_client.application.extensions,
        "command_dispatcher",
        dispatcher,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/receive",
        data=_receiving_form_data(),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert len(dispatcher.calls) == 1

    command, context = dispatcher.calls[0]

    assert command.purchase_order_id == purchase_order.id
    assert command.purchase_order_reference == purchase_order.reference
    assert command.purchase_order_line_reference == (
        f"PO-LINE-{line.guid}"
    )
    assert command.stock_item_reference == "WATER-500ML"
    assert command.purchase_order_line_reference != (
        command.stock_item_reference
    )


def test_receive_purchase_order_blocks_line_without_inventory_mapping(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    """A line without an Inventory Product mapping must not be dispatched."""
    from app.modules.procurement.routes import routes

    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_order.receive",
    )

    purchase_order, _line = _purchase_order(
        stock_item_reference=None,
    )

    class FakePurchaseOrderService:
        def get_by_id(self, purchase_order_id):
            assert purchase_order_id == 1
            return purchase_order

    class FakeCommandDispatcher:
        def __init__(self):
            self.calls = []

        def dispatch(self, command, context):
            self.calls.append((command, context))
            raise AssertionError(
                "A receipt must not be dispatched without an Inventory mapping."
            )

    dispatcher = FakeCommandDispatcher()

    monkeypatch.setattr(
        routes,
        "PurchaseOrderService",
        FakePurchaseOrderService,
    )
    monkeypatch.setitem(
        authenticated_client.application.extensions,
        "command_dispatcher",
        dispatcher,
    )

    response = authenticated_client.post(
        "/procurement/purchase-orders/1/receive",
        data=_receiving_form_data(),
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert dispatcher.calls == []
