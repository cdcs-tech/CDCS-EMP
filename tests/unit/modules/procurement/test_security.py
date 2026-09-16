"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Permission definition tests.
"""

from app.core.security import Permission
from app.modules.procurement.security import (
    PROCUREMENT_PERMISSIONS,
    PROCUREMENT_PURCHASE_REQUEST_APPROVE,
    PROCUREMENT_PURCHASE_REQUEST_REJECT,
    PROCUREMENT_PURCHASE_REQUEST_RETURN,
    PROCUREMENT_PURCHASE_REQUEST_SUBMIT,
    PROCUREMENT_PURCHASE_REQUIREMENT_CREATE,
    PROCUREMENT_PURCHASE_REQUIREMENT_DELETE,
    PROCUREMENT_PURCHASE_REQUIREMENT_READ,
    PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE,
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


def test_purchase_request_workflow_permissions_use_enterprise_permission_contract():
    """
    Verify that all Purchase Request workflow permissions use
    the enterprise Permission contract.
    """

    permissions = [
        PROCUREMENT_PURCHASE_REQUEST_SUBMIT,
        PROCUREMENT_PURCHASE_REQUEST_APPROVE,
        PROCUREMENT_PURCHASE_REQUEST_REJECT,
        PROCUREMENT_PURCHASE_REQUEST_RETURN,
    ]

    assert all(
        isinstance(permission, Permission)
        for permission in permissions
    )


def test_purchase_request_workflow_permissions_have_expected_identity():
    """
    Verify the approved Purchase Request workflow permission identities.
    """

    assert (
        PROCUREMENT_PURCHASE_REQUEST_SUBMIT.code
        == "PROCUREMENT.PURCHASE_REQUEST.SUBMIT"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_SUBMIT.name
        == "procurement.purchase_request.submit"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_SUBMIT.resource
        == "purchase_request"
    )
    assert PROCUREMENT_PURCHASE_REQUEST_SUBMIT.action == "submit"

    assert (
        PROCUREMENT_PURCHASE_REQUEST_APPROVE.code
        == "PROCUREMENT.PURCHASE_REQUEST.APPROVE"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_APPROVE.name
        == "procurement.purchase_request.approve"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_APPROVE.resource
        == "purchase_request"
    )
    assert PROCUREMENT_PURCHASE_REQUEST_APPROVE.action == "approve"

    assert (
        PROCUREMENT_PURCHASE_REQUEST_REJECT.code
        == "PROCUREMENT.PURCHASE_REQUEST.REJECT"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_REJECT.name
        == "procurement.purchase_request.reject"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_REJECT.resource
        == "purchase_request"
    )
    assert PROCUREMENT_PURCHASE_REQUEST_REJECT.action == "reject"

    assert (
        PROCUREMENT_PURCHASE_REQUEST_RETURN.code
        == "PROCUREMENT.PURCHASE_REQUEST.RETURN"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_RETURN.name
        == "procurement.purchase_request.return"
    )
    assert (
        PROCUREMENT_PURCHASE_REQUEST_RETURN.resource
        == "purchase_request"
    )
    assert PROCUREMENT_PURCHASE_REQUEST_RETURN.action == "return"


def test_procurement_permissions_contains_currently_defined_permissions():
    """
    Verify that the Procurement aggregate contains all currently
    approved Supplier, PurchaseRequirement, and PurchaseRequest
    workflow permissions.
    """

    assert PROCUREMENT_PERMISSIONS == (
        PROCUREMENT_SUPPLIER_CREATE,
        PROCUREMENT_SUPPLIER_READ,
        PROCUREMENT_SUPPLIER_UPDATE,
        PROCUREMENT_SUPPLIER_DELETE,
        PROCUREMENT_PURCHASE_REQUIREMENT_CREATE,
        PROCUREMENT_PURCHASE_REQUIREMENT_READ,
        PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE,
        PROCUREMENT_PURCHASE_REQUIREMENT_DELETE,
        PROCUREMENT_PURCHASE_REQUEST_SUBMIT,
        PROCUREMENT_PURCHASE_REQUEST_APPROVE,
        PROCUREMENT_PURCHASE_REQUEST_REJECT,
        PROCUREMENT_PURCHASE_REQUEST_RETURN,
    )


def test_procurement_permissions_use_procurement_module_boundary():
    """
    Verify that all Procurement permissions remain owned by Procurement.
    """

    for permission in PROCUREMENT_PERMISSIONS:
        assert permission.module == "PROCUREMENT"


def test_supplier_permissions_expose_no_workflow_actions():
    """
    Verify that Supplier permissions remain CRUD-only and expose
    no workflow actions.
    """

    supplier_permissions = (
        PROCUREMENT_SUPPLIER_CREATE,
        PROCUREMENT_SUPPLIER_READ,
        PROCUREMENT_SUPPLIER_UPDATE,
        PROCUREMENT_SUPPLIER_DELETE,
    )

    actions = {
        permission.action
        for permission in supplier_permissions
    }

    assert actions == {
        "create",
        "read",
        "update",
        "delete",
    }
