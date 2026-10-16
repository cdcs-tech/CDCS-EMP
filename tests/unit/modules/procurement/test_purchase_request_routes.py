"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase request route tests.
"""

from __future__ import annotations

import pytest

from types import SimpleNamespace

from datetime import date

from app.modules.procurement.models import PurchaseRequest
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


def test_purchase_request_list_requires_login(
    client,
):
    response = client.get(
        "/procurement/purchase-requests/",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_purchase_request_list_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requests/",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_request_list_route_is_registered(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request.read",
    )

    captured = {}

    class FakePurchaseRequestService:
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
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-requests/"
        "?search=food"
        "&status=DRAFT"
        "&sort=reference"
        "&direction=desc"
        "&page=2"
        "&page_size=10"
    )

    assert response.status_code == 200
    assert captured["template"] == (
        "modules/procurement/purchase_requests/index.html"
    )
    assert captured["context"]["purchase_requests"] == "result"
    assert captured["context"]["can_create_purchase_request"] is False
    assert captured["context"]["can_update_purchase_request"] is False
    assert captured["context"]["can_delete_purchase_request"] is False

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 10
    assert options.sort_by == "reference"
    assert options.sort_direction == "desc"
    assert options.search == "food"
    assert options.filters == {"status": "DRAFT"}


def test_purchase_request_create_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requests/create",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_request_create_submits_valid_request(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request.create",
    )

    created = {}

    class FakePurchaseRequestService:
        def create(self, entity):
            created["entity"] = entity
            return entity

    class FakePurchaseRequirement:
        def __init__(
            self,
            requirement_id,
            reference,
        ):
            self.id = requirement_id
            self.reference = reference

    class FakePurchaseRequirementService:
        def paginate(self, options):
            class Result:
                items = [
                    FakePurchaseRequirement(
                        1,
                        "PR-001",
                    ),
                ]

            return Result()

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/create",
        data={
            "reference": "PReq-001",
            "purchase_requirement_id": "1",
            "request_date": "2026-09-15",
            "required_by_date": "2026-09-30",
            "status": "APPROVED",
            "justification": "Catering supplies required.",
            "notes": "Initial procurement request.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requests/"
    )

    entity = created["entity"]

    assert entity.reference == "PReq-001"
    assert entity.purchase_requirement_id == 1
    assert entity.request_date == date(2026, 9, 15)
    assert entity.required_by_date == date(2026, 9, 30)
    assert entity.status == "DRAFT"
    assert entity.justification == (
        "Catering supplies required."
    )
    assert entity.notes == (
        "Initial procurement request."
    )


def test_purchase_request_view_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requests/1",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_request_view_renders_for_authorized_user(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request.read",
    )

    for permission_name in (
        "procurement.purchase_request.submit",
        "procurement.purchase_request.approve",
        "procurement.purchase_request.reject",
        "procurement.purchase_request.return",
    ):
        _grant_permission(
            session,
            admin_user,
            permission_name,
        )

    purchase_request = PurchaseRequest(
        id=1,
        reference="PReq-VIEW-001",
        purchase_requirement_id=7,
        request_date=date(2026, 9, 15),
        required_by_date=date(2026, 9, 30),
        status="DRAFT",
        justification="Food supplies.",
        notes="View test.",
    )

    captured = {}

    class FakePurchaseRequestService:
        def get(self, purchase_request_id):
            assert purchase_request_id == 1
            return purchase_request

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-requests/1",
    )

    assert response.status_code == 200
    assert captured["template"] == (
        "modules/procurement/purchase_requests/view.html"
    )
    assert (
        captured["context"]["purchase_request"]
        is purchase_request
    )
    assert captured["context"]["can_submit_purchase_request"] is True
    assert captured["context"]["can_approve_purchase_request"] is True
    assert captured["context"]["can_reject_purchase_request"] is True
    assert captured["context"]["can_return_purchase_request"] is True


def test_purchase_request_edit_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requests/1/edit",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_request_edit_submits_updated_request(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request.update",
    )

    purchase_request = PurchaseRequest(
        id=1,
        reference="PReq-EDIT-001",
        purchase_requirement_id=7,
        request_date=date(2026, 9, 15),
        required_by_date=date(2026, 9, 30),
        status="SUBMITTED",
        justification="Original request.",
        notes="Original notes.",
    )

    updated = {}

    class FakePurchaseRequestService:
        def get(self, purchase_request_id):
            assert purchase_request_id == 1
            return purchase_request

        def update(self, entity):
            updated["entity"] = entity
            return entity

    class FakePurchaseRequirement:
        def __init__(
            self,
            requirement_id,
            reference,
        ):
            self.id = requirement_id
            self.reference = reference

    class FakePurchaseRequirementService:
        def paginate(self, options):
            class Result:
                items = [
                    FakePurchaseRequirement(
                        7,
                        "PR-007",
                    ),
                    FakePurchaseRequirement(
                        8,
                        "PR-008",
                    ),
                ]

            return Result()

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/1/edit",
        data={
            "reference": "PReq-EDIT-002",
            "purchase_requirement_id": "8",
            "request_date": "2026-09-20",
            "required_by_date": "2026-10-15",
            "status": "APPROVED",
            "justification": "Updated request.",
            "notes": "Updated notes.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requests/1"
    )

    entity = updated["entity"]

    assert entity.reference == "PReq-EDIT-002"
    assert entity.purchase_requirement_id == 8
    assert entity.request_date == date(2026, 9, 20)
    assert entity.required_by_date == date(2026, 10, 15)
    assert entity.status == "SUBMITTED"
    assert entity.justification == "Updated request."
    assert entity.notes == "Updated notes."


def test_purchase_request_delete_requires_permission(
    authenticated_client,
):
    response = authenticated_client.post(
        "/procurement/purchase-requests/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_request_delete_submits_delete(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_request.delete",
    )

    deleted = {}

    class FakePurchaseRequestService:
        def delete(self, purchase_request_id):
            deleted["id"] = purchase_request_id

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequestService",
        FakePurchaseRequestService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requests/7/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requests/"
    )
    assert deleted["id"] == 7


@pytest.mark.parametrize(
    (
        "action",
        "permission_name",
        "expected_command",
        "expected_operation",
    ),
    [
        (
            "submit",
            "procurement.purchase_request.submit",
            "SubmitPurchaseRequestCommand",
            "procurement.purchase_request.submit",
        ),
        (
            "approve",
            "procurement.purchase_request.approve",
            "ApprovePurchaseRequestCommand",
            "procurement.purchase_request.approve",
        ),
        (
            "reject",
            "procurement.purchase_request.reject",
            "RejectPurchaseRequestCommand",
            "procurement.purchase_request.reject",
        ),
        (
            "return",
            "procurement.purchase_request.return",
            "ReturnPurchaseRequestCommand",
            "procurement.purchase_request.return",
        ),
    ],
)
def test_purchase_request_workflow_route_dispatches_command(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
    action,
    permission_name,
    expected_command,
    expected_operation,
):
    _grant_permission(
        session,
        admin_user,
        permission_name,
    )

    captured = {}

    class FakeDispatcher:
        def dispatch(self, command, context):
            captured["command"] = command
            captured["context"] = context
            return SimpleNamespace(
                success=True,
                message="Workflow action completed.",
            )

    monkeypatch.setitem(
        authenticated_client.application.extensions,
        "command_dispatcher",
        FakeDispatcher(),
    )

    response = authenticated_client.post(
        f"/procurement/purchase-requests/7/{action}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requests/7"
    )
    assert type(captured["command"]).__name__ == expected_command
    assert captured["command"].purchase_request_id == 7
    assert captured["context"].module_name == "PROCUREMENT"
    assert captured["context"].operation == expected_operation


@pytest.mark.parametrize(
    "action",
    [
        "submit",
        "approve",
        "reject",
        "return",
    ],
)
def test_purchase_request_workflow_route_requires_permission(
    authenticated_client,
    action,
):
    response = authenticated_client.post(
        f"/procurement/purchase-requests/7/{action}",
        follow_redirects=False,
    )

    assert response.status_code == 403


@pytest.mark.parametrize("action", ["submit", "approve", "reject", "return"])
def test_purchase_request_workflow_routes_reject_get_requests(
    authenticated_client,
    action,
):
    response = authenticated_client.get(
        f"/procurement/purchase-requests/7/{action}",
        follow_redirects=False,
    )

    assert response.status_code == 405
