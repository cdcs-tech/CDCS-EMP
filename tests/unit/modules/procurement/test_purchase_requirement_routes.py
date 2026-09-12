"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase requirement route tests.
"""

from __future__ import annotations

from datetime import date

from app.modules.procurement.models import PurchaseRequirement
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


def test_purchase_requirement_list_requires_login(
    client,
):
    response = client.get(
        "/procurement/purchase-requirements/",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_purchase_requirement_list_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requirements/",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_requirement_list_route_is_registered(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_requirement.read",
    )

    captured = {}

    class FakePurchaseRequirementService:
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
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-requirements/"
        "?search=food"
        "&status=DRAFT"
        "&sort=reference"
        "&direction=desc"
        "&page=2"
        "&page_size=10"
    )

    assert response.status_code == 200
    assert captured["template"] == (
        "modules/procurement/purchase_requirements/index.html"
    )
    assert captured["context"]["purchase_requirements"] == "result"

    options = captured["options"]

    assert options.page == 2
    assert options.page_size == 10
    assert options.sort_by == "reference"
    assert options.sort_direction == "desc"
    assert options.search == "food"
    assert options.filters == {"status": "DRAFT"}


def test_purchase_requirement_create_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requirements/create",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_requirement_create_submits_valid_requirement(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_requirement.create",
    )

    created = {}

    class FakePurchaseRequirementService:
        def create(self, entity):
            created["entity"] = entity
            return entity

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requirements/create",
        data={
            "reference": "PR-001",
            "description": "Food supplies required for catering.",
            "source_module": "CATERING",
            "source_type": "Event",
            "source_reference": "EVT-001",
            "required_by_date": "2026-09-30",
            "status": "DRAFT",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requirements/"
    )

    entity = created["entity"]

    assert entity.reference == "PR-001"
    assert entity.description == (
        "Food supplies required for catering."
    )
    assert entity.source_module == "CATERING"
    assert entity.source_type == "Event"
    assert entity.source_reference == "EVT-001"
    assert entity.required_by_date == date(2026, 9, 30)
    assert entity.status == "DRAFT"


def test_purchase_requirement_view_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requirements/1",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_requirement_view_renders_for_authorized_user(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_requirement.read",
    )

    purchase_requirement = PurchaseRequirement(
        id=1,
        reference="PR-VIEW-001",
        description="Food supplies.",
        source_module="CATERING",
        source_type="Event",
        source_reference="EVT-001",
        required_by_date=date(2026, 9, 30),
        status="DRAFT",
    )

    captured = {}

    class FakePurchaseRequirementService:
        def get(self, purchase_requirement_id):
            assert purchase_requirement_id == 1
            return purchase_requirement

    def fake_render_template(
        template,
        **context,
    ):
        captured["template"] = template
        captured["context"] = context
        return "rendered"

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )
    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.render_template",
        fake_render_template,
    )

    response = authenticated_client.get(
        "/procurement/purchase-requirements/1",
    )

    assert response.status_code == 200
    assert captured["template"] == (
        "modules/procurement/purchase_requirements/view.html"
    )
    assert (
        captured["context"]["purchase_requirement"]
        is purchase_requirement
    )


def test_purchase_requirement_edit_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/purchase-requirements/1/edit",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_requirement_edit_submits_updated_requirement(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_requirement.update",
    )

    purchase_requirement = PurchaseRequirement(
        id=1,
        reference="PR-EDIT-001",
        description="Original requirement.",
        source_module="CATERING",
        source_type="Event",
        source_reference="EVT-001",
        required_by_date=date(2026, 9, 30),
        status="DRAFT",
    )

    updated = {}

    class FakePurchaseRequirementService:
        def get(self, purchase_requirement_id):
            assert purchase_requirement_id == 1
            return purchase_requirement

        def update(self, entity):
            updated["entity"] = entity
            return entity

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requirements/1/edit",
        data={
            "reference": "PR-EDIT-002",
            "description": "Updated requirement.",
            "source_module": "CATERING",
            "source_type": "Event",
            "source_reference": "EVT-002",
            "required_by_date": "2026-10-15",
            "status": "DRAFT",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requirements/1"
    )

    entity = updated["entity"]

    assert entity.reference == "PR-EDIT-002"
    assert entity.description == "Updated requirement."
    assert entity.source_module == "CATERING"
    assert entity.source_type == "Event"
    assert entity.source_reference == "EVT-002"
    assert entity.required_by_date == date(2026, 10, 15)
    assert entity.status == "DRAFT"


def test_purchase_requirement_delete_requires_permission(
    authenticated_client,
):
    response = authenticated_client.post(
        "/procurement/purchase-requirements/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_purchase_requirement_delete_submits_delete(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.purchase_requirement.delete",
    )

    deleted = {}

    class FakePurchaseRequirementService:
        def delete(self, purchase_requirement_id):
            deleted["id"] = purchase_requirement_id

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.PurchaseRequirementService",
        FakePurchaseRequirementService,
    )

    response = authenticated_client.post(
        "/procurement/purchase-requirements/7/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/purchase-requirements/"
    )
    assert deleted["id"] == 7
