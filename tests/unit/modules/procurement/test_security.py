"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Supplier security permission tests.
"""

from app.core.security import Permission
from app.modules.procurement.security import (
    PROCUREMENT_PERMISSIONS,
    PROCUREMENT_SUPPLIER_CREATE,
    PROCUREMENT_SUPPLIER_DELETE,
    PROCUREMENT_SUPPLIER_READ,
    PROCUREMENT_SUPPLIER_UPDATE,
)


def test_supplier_permissions_use_enterprise_permission_contract():
    """
    Verify that all Supplier permissions use the enterprise
    Permission contract.
    """

    permissions = [
        PROCUREMENT_SUPPLIER_CREATE,
        PROCUREMENT_SUPPLIER_READ,
        PROCUREMENT_SUPPLIER_UPDATE,
        PROCUREMENT_SUPPLIER_DELETE,
    ]

    assert all(
        isinstance(permission, Permission)
        for permission in permissions
    )


def test_supplier_permissions_have_expected_identity():
    """
    Verify the approved Supplier permission identities.
    """

    assert PROCUREMENT_SUPPLIER_CREATE.code == "PROCUREMENT.SUPPLIER.CREATE"
    assert PROCUREMENT_SUPPLIER_CREATE.name == "procurement.supplier.create"
    assert PROCUREMENT_SUPPLIER_CREATE.resource == "supplier"
    assert PROCUREMENT_SUPPLIER_CREATE.action == "create"

    assert PROCUREMENT_SUPPLIER_READ.code == "PROCUREMENT.SUPPLIER.READ"
    assert PROCUREMENT_SUPPLIER_READ.name == "procurement.supplier.read"
    assert PROCUREMENT_SUPPLIER_READ.resource == "supplier"
    assert PROCUREMENT_SUPPLIER_READ.action == "read"

    assert PROCUREMENT_SUPPLIER_UPDATE.code == "PROCUREMENT.SUPPLIER.UPDATE"
    assert PROCUREMENT_SUPPLIER_UPDATE.name == "procurement.supplier.update"
    assert PROCUREMENT_SUPPLIER_UPDATE.resource == "supplier"
    assert PROCUREMENT_SUPPLIER_UPDATE.action == "update"

    assert PROCUREMENT_SUPPLIER_DELETE.code == "PROCUREMENT.SUPPLIER.DELETE"
    assert PROCUREMENT_SUPPLIER_DELETE.name == "procurement.supplier.delete"
    assert PROCUREMENT_SUPPLIER_DELETE.resource == "supplier"
    assert PROCUREMENT_SUPPLIER_DELETE.action == "delete"


def test_procurement_permissions_contains_only_currently_defined_permissions():
    """
    Verify that the Procurement aggregate currently contains
    only the approved Supplier permissions.
    """

    assert PROCUREMENT_PERMISSIONS == (
        PROCUREMENT_SUPPLIER_CREATE,
        PROCUREMENT_SUPPLIER_READ,
        PROCUREMENT_SUPPLIER_UPDATE,
        PROCUREMENT_SUPPLIER_DELETE,
    )


def test_supplier_permissions_use_procurement_module_boundary():
    """
    Verify that Supplier permissions remain owned by Procurement.
    """

    for permission in PROCUREMENT_PERMISSIONS:
        assert permission.module == "PROCUREMENT"


def test_supplier_permissions_expose_no_workflow_actions():
    """
    Verify that workflow-specific actions remain deferred.
    """

    actions = {
        permission.action
        for permission in PROCUREMENT_PERMISSIONS
    }

    assert actions == {
        "create",
        "read",
        "update",
        "delete",
    }
