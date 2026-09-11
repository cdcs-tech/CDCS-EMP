"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Supplier route tests.
"""

from __future__ import annotations

import pytest

from app.modules.procurement.models import Supplier
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


def test_supplier_list_requires_login(
    client,
):
    """
    Verify that the Supplier list requires authentication.
    """

    response = client.get(
        "/procurement/suppliers/",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_supplier_list_requires_permission(authenticated_client):
    response = authenticated_client.get(
        "/procurement/suppliers/",
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_supplier_list_route_is_registered(
    app,
    session,
    admin_user,
    authenticated_client,
):
    """
    Verify that the Supplier list route is registered and
    accessible when the required permission is granted.
    """

    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.read",
    )

    response = authenticated_client.get(
        "/procurement/suppliers/"
    )

    assert response.status_code == 200


def test_supplier_create_requires_permission(authenticated_client):
    response = authenticated_client.get(
        "/procurement/suppliers/create",
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_supplier_create_route_renders_for_authorized_user(
    app,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.create",
    )

    response = authenticated_client.get(
        "/procurement/suppliers/create",
    )

    assert response.status_code == 200
    assert b"New Supplier" in response.data
    assert b"Create Supplier" in response.data


def test_supplier_create_submits_valid_supplier(
    monkeypatch,
    authenticated_client,
    session,
    admin_user,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.create",
    )

    created = {}

    class FakeSupplierService:
        def create(self, entity):
            created["entity"] = entity
            return entity

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    response = authenticated_client.post(
        "/procurement/suppliers/create",
        data={
            "name": "Test Catering Supplier",
            "code": "SUP-001",
            "supplier_type": "Food Supplier",
            "contact_information": "+211 912 345 678",
            "address_information": "Juba, South Sudan",
            "status": "ACTIVE",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/suppliers/"
    )

    entity = created["entity"]

    assert entity.name == "Test Catering Supplier"
    assert entity.code == "SUP-001"
    assert entity.supplier_type == "Food Supplier"
    assert entity.contact_information == "+211 912 345 678"
    assert entity.address_information == "Juba, South Sudan"
    assert entity.status == "ACTIVE"

def test_supplier_view_requires_login(
    client,
):
    response = client.get(
        "/procurement/suppliers/1",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_supplier_view_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/suppliers/1",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_supplier_view_renders_for_authorized_user(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.read",
    )

    supplier = Supplier(
        id=1,
        name="Test Supplier",
        code="SUP-VIEW-001",
        supplier_type="Food Supplier",
        contact_information="+211 912 345 678",
        address_information="Juba, South Sudan",
        status="ACTIVE",
    )

    class FakeSupplierService:
        def get(self, supplier_id):
            assert supplier_id == 1
            return supplier

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    response = authenticated_client.get(
        "/procurement/suppliers/1",
    )

    assert response.status_code == 200
    assert b"Supplier Details" in response.data
    assert b"SUP-VIEW-001" in response.data
    assert b"Test Supplier" in response.data


def test_supplier_edit_requires_permission(
    authenticated_client,
):
    response = authenticated_client.get(
        "/procurement/suppliers/1/edit",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_supplier_edit_renders_for_authorized_user(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.update",
    )

    supplier = Supplier(
        id=1,
        name="Existing Supplier",
        code="SUP-EDIT-001",
        supplier_type="Food Supplier",
        contact_information="+211 912 345 678",
        address_information="Juba, South Sudan",
        status="ACTIVE",
    )

    class FakeSupplierService:
        def get(self, supplier_id):
            assert supplier_id == 1
            return supplier

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    response = authenticated_client.get(
        "/procurement/suppliers/1/edit",
    )

    assert response.status_code == 200
    assert b"Edit Supplier" in response.data
    assert b"Existing Supplier" in response.data
    assert b"SUP-EDIT-001" in response.data


def test_supplier_edit_submits_updated_supplier(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.update",
    )

    supplier = Supplier(
        id=1,
        name="Existing Supplier",
        code="SUP-EDIT-001",
        supplier_type="Food Supplier",
        contact_information="+211 912 345 678",
        address_information="Juba, South Sudan",
        status="ACTIVE",
    )

    updated = {}

    class FakeSupplierService:
        def get(self, supplier_id):
            assert supplier_id == 1
            return supplier

        def update(self, entity):
            updated["entity"] = entity
            return entity

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    response = authenticated_client.post(
        "/procurement/suppliers/1/edit",
        data={
            "name": "Updated Supplier",
            "code": "SUP-EDIT-002",
            "supplier_type": "Equipment Supplier",
            "contact_information": "+211 987 654 321",
            "address_information": "Juba, South Sudan",
            "status": "ACTIVE",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/suppliers/1"
    )

    entity = updated["entity"]

    assert entity.name == "Updated Supplier"
    assert entity.code == "SUP-EDIT-002"
    assert entity.supplier_type == "Equipment Supplier"
    assert entity.contact_information == "+211 987 654 321"
    assert entity.address_information == "Juba, South Sudan"
    assert entity.status == "ACTIVE"


def test_supplier_delete_requires_permission(
    authenticated_client,
):
    response = authenticated_client.post(
        "/procurement/suppliers/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 403


def test_supplier_delete_submits_entity_for_deletion(
    monkeypatch,
    session,
    admin_user,
    authenticated_client,
):
    _grant_permission(
        session,
        admin_user,
        "procurement.supplier.delete",
    )

    supplier = Supplier(
        id=1,
        name="Supplier To Delete",
        code="SUP-DELETE-001",
        supplier_type="Food Supplier",
        contact_information="+211 912 345 678",
        address_information="Juba, South Sudan",
        status="ACTIVE",
    )

    deleted = {}

    class FakeSupplierService:
        def delete(self, supplier_id):
            deleted["supplier_id"] = supplier_id

    monkeypatch.setattr(
        "app.modules.procurement.routes.routes.SupplierService",
        FakeSupplierService,
    )

    response = authenticated_client.post(
        "/procurement/suppliers/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith(
        "/procurement/suppliers/"
    )
    assert deleted["supplier_id"] == 1
