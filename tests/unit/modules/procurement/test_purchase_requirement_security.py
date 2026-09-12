"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase requirement permission tests.
"""

from app.modules.procurement.security import (
    PROCUREMENT_PURCHASE_REQUIREMENT_CREATE,
    PROCUREMENT_PURCHASE_REQUIREMENT_DELETE,
    PROCUREMENT_PURCHASE_REQUIREMENT_READ,
    PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE,
)


def test_purchase_requirement_create_permission():
    permission = PROCUREMENT_PURCHASE_REQUIREMENT_CREATE

    assert permission.code == "PROCUREMENT.PURCHASE_REQUIREMENT.CREATE"
    assert permission.name == "procurement.purchase_requirement.create"
    assert permission.module == "PROCUREMENT"
    assert permission.resource == "purchase_requirement"
    assert permission.action == "create"


def test_purchase_requirement_read_permission():
    permission = PROCUREMENT_PURCHASE_REQUIREMENT_READ

    assert permission.code == "PROCUREMENT.PURCHASE_REQUIREMENT.READ"
    assert permission.name == "procurement.purchase_requirement.read"
    assert permission.module == "PROCUREMENT"
    assert permission.resource == "purchase_requirement"
    assert permission.action == "read"


def test_purchase_requirement_update_permission():
    permission = PROCUREMENT_PURCHASE_REQUIREMENT_UPDATE

    assert permission.code == "PROCUREMENT.PURCHASE_REQUIREMENT.UPDATE"
    assert permission.name == "procurement.purchase_requirement.update"
    assert permission.module == "PROCUREMENT"
    assert permission.resource == "purchase_requirement"
    assert permission.action == "update"


def test_purchase_requirement_delete_permission():
    permission = PROCUREMENT_PURCHASE_REQUIREMENT_DELETE

    assert permission.code == "PROCUREMENT.PURCHASE_REQUIREMENT.DELETE"
    assert permission.name == "procurement.purchase_requirement.delete"
    assert permission.module == "PROCUREMENT"
    assert permission.resource == "purchase_requirement"
    assert permission.action == "delete"
