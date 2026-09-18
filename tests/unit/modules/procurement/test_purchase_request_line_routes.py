from datetime import date
from types import SimpleNamespace

from app.models.role_permission import RolePermission
from tests.factories.permission_factory import PermissionFactory


def _grant_permission(
    session,
    admin_user,
    permission_name,
):
    permission = PermissionFactory.create(
        session=session,
        module="PROCUREMENT",
        name=permission_name,
        description=f"Test permission: {permission_name}",
        commit=False,
    )

    session.add(permission)

    role_permission = RolePermission(
        role=admin_user.user_roles[0].role,
        permission_id=permission.id,
    )

    session.add(role_permission)
    session.commit()


def test_create_purchase_request_line_requires_login(client):
    response = client.get(
        "/procurement/purchase-requests/1/lines/create"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_create_purchase_request_line_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requests/1/lines/create"
    )

    assert response.status_code == 403


def test_create_purchase_request_line_renders_form(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request_line.create",
    )

    purchase_request = SimpleNamespace(
        id=1,
        reference="PR-001",
    )

    class FakePurchaseRequestService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_request

    captured = {}

    def fake_render_template(template, **context):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        routes,
        "render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-requests/1/lines/create"
    )

    assert response.status_code == 200
    assert captured["template"] == (
        "modules/procurement/purchase_requests/line_form.html"
    )
    assert captured["context"]["purchase_request"] is purchase_request
    assert captured["context"]["page_title"] == (
        "Add Purchase Request Line"
    )


def test_create_purchase_request_line_creates_line(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request_line.create",
    )

    purchase_request = SimpleNamespace(
        id=1,
        reference="PR-001",
    )

    created = {}

    class FakePurchaseRequestService:
        def get(self, entity_id):
            assert entity_id == 1
            return purchase_request

    class FakePurchaseRequestLineService:
        def create(self, line):
            created["line"] = line
            return line

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        routes,
        "PurchaseRequestLineService",
        FakePurchaseRequestLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/1/lines/create",
        data={
            "description": "Office stationery",
            "item_reference": "STAT-001",
            "quantity": "10.000",
            "unit": "pack",
            "estimated_unit_cost": "25.50",
            "estimated_total": "255.00",
            "required_by_date": "2026-10-15",
            "notes": "Required for office operations.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/procurement/purchase-requests/1" in (
        response.headers["Location"]
    )

    line = created["line"]

    assert line.purchase_request_id == 1
    assert line.description == "Office stationery"
    assert line.item_reference == "STAT-001"
    assert str(line.quantity) == "10.000"
    assert line.unit == "pack"
    assert str(line.estimated_unit_cost) == "25.50"
    assert str(line.estimated_total) == "255.00"
    assert line.required_by_date == date(2026, 10, 15)
    assert line.notes == "Required for office operations."


def test_edit_purchase_request_line_requires_login(client):
    response = client.get(
        "/procurement/purchase-requests/1/lines/2/edit"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_edit_purchase_request_line_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requests/1/lines/2/edit"
    )

    assert response.status_code == 403


def test_edit_purchase_request_line_rejects_wrong_parent(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request_line.update",
    )

    purchase_request = SimpleNamespace(
        id=1,
        reference="PR-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_request_id=99,
    )

    class FakePurchaseRequestService:
        def get(self, entity_id):
            return purchase_request

    class FakePurchaseRequestLineService:
        def get(self, entity_id):
            return line

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        routes,
        "PurchaseRequestLineService",
        FakePurchaseRequestLineService,
    )

    response = authenticated_client.get(
        "/procurement/purchase-requests/1/lines/2/edit"
    )

    assert response.status_code == 404


def test_edit_purchase_request_line_updates_line(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request_line.update",
    )

    purchase_request = SimpleNamespace(
        id=1,
        reference="PR-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_request_id=1,
        description="Old description",
        item_reference="OLD-001",
        quantity=2,
        unit="box",
        estimated_unit_cost=10,
        estimated_total=20,
        required_by_date=date(2026, 10, 1),
        notes="Old notes",
    )

    updated = {}

    class FakePurchaseRequestService:
        def get(self, entity_id):
            return purchase_request

    class FakePurchaseRequestLineService:
        def get(self, entity_id):
            assert entity_id == 2
            return line

        def update(self, entity):
            updated["line"] = entity
            return entity

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        routes,
        "PurchaseRequestLineService",
        FakePurchaseRequestLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/1/lines/2/edit",
        data={
            "description": "Updated stationery",
            "item_reference": "STAT-002",
            "quantity": "5.000",
            "unit": "carton",
            "estimated_unit_cost": "30.00",
            "estimated_total": "150.00",
            "required_by_date": "2026-11-01",
            "notes": "Updated requirement.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/procurement/purchase-requests/1" in (
        response.headers["Location"]
    )

    assert updated["line"] is line
    assert line.purchase_request_id == 1
    assert line.description == "Updated stationery"
    assert line.item_reference == "STAT-002"
    assert str(line.quantity) == "5.000"
    assert line.unit == "carton"
    assert str(line.estimated_unit_cost) == "30.00"
    assert str(line.estimated_total) == "150.00"
    assert line.required_by_date == date(2026, 11, 1)
    assert line.notes == "Updated requirement."


def test_delete_purchase_request_line_requires_login(client):
    response = client.post(
        "/procurement/purchase-requests/1/lines/2/delete"
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_delete_purchase_request_line_requires_permission(
    authenticated_client,
):
    response = authenticated_client.post(
        "/procurement/purchase-requests/1/lines/2/delete"
    )

    assert response.status_code == 403


def test_delete_purchase_request_line_rejects_wrong_parent(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request_line.delete",
    )

    purchase_request = SimpleNamespace(
        id=1,
        reference="PR-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_request_id=99,
    )

    class FakePurchaseRequestService:
        def get(self, entity_id):
            return purchase_request

    class FakePurchaseRequestLineService:
        def get(self, entity_id):
            return line

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        routes,
        "PurchaseRequestLineService",
        FakePurchaseRequestLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/1/lines/2/delete"
    )

    assert response.status_code == 404


def test_delete_purchase_request_line_deletes_line(
    authenticated_client,
    admin_user,
    session,
    monkeypatch,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request_line.delete",
    )

    purchase_request = SimpleNamespace(
        id=1,
        reference="PR-001",
    )

    line = SimpleNamespace(
        id=2,
        purchase_request_id=1,
    )

    deleted = {}

    class FakePurchaseRequestService:
        def get(self, entity_id):
            return purchase_request

    class FakePurchaseRequestLineService:
        def get(self, entity_id):
            assert entity_id == 2
            return line

        def delete(self, entity_id):
            deleted["id"] = entity_id

    from app.modules.procurement.routes import routes

    monkeypatch.setattr(
        routes,
        "PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        routes,
        "PurchaseRequestLineService",
        FakePurchaseRequestLineService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/1/lines/2/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/procurement/purchase-requests/1" in (
        response.headers["Location"]
    )
    assert deleted["id"] == 2
