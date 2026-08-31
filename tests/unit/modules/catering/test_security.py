"""
Catering security and governance tests.
"""

import pytest

from app.core.security import Permission
from app.core.security.registry import permission_registry

from app.modules.catering import CateringModule
from app.modules.catering.security import (
    CATERING_PERMISSIONS,
    CATERING_PRODUCT_CATEGORY_CREATE,
    CATERING_PRODUCT_CATEGORY_READ,
    CATERING_PRODUCT_CATEGORY_UPDATE,
    CATERING_PRODUCT_CATEGORY_DELETE,
    CATERING_PRODUCT_CREATE,
    CATERING_PRODUCT_READ,
    CATERING_PRODUCT_UPDATE,
    CATERING_PRODUCT_DELETE,
)


def test_catering_permissions_are_permission_objects():
    """
    Every Catering permission must use the enterprise
    Permission contract.
    """

    assert len(CATERING_PERMISSIONS) == 8

    assert all(
        isinstance(permission, Permission)
        for permission in CATERING_PERMISSIONS
    )


def test_catering_permission_codes_are_unique():
    """
    Catering permission codes must be unique.
    """

    codes = [
        permission.code
        for permission in CATERING_PERMISSIONS
    ]

    assert len(codes) == len(set(codes))


def test_catering_permission_names_are_unique():
    """
    Catering permission names must be unique.
    """

    names = [
        permission.name
        for permission in CATERING_PERMISSIONS
    ]

    assert len(names) == len(set(names))


@pytest.mark.parametrize(
    "permission, code, name, resource, action",
    [
        (
            CATERING_PRODUCT_CATEGORY_CREATE,
            "CATERING.PRODUCT_CATEGORY.CREATE",
            "catering.product_category.create",
            "product_category",
            "create",
        ),
        (
            CATERING_PRODUCT_CATEGORY_READ,
            "CATERING.PRODUCT_CATEGORY.READ",
            "catering.product_category.read",
            "product_category",
            "read",
        ),
        (
            CATERING_PRODUCT_CATEGORY_UPDATE,
            "CATERING.PRODUCT_CATEGORY.UPDATE",
            "catering.product_category.update",
            "product_category",
            "update",
        ),
        (
            CATERING_PRODUCT_CATEGORY_DELETE,
            "CATERING.PRODUCT_CATEGORY.DELETE",
            "catering.product_category.delete",
            "product_category",
            "delete",
        ),
        (
            CATERING_PRODUCT_CREATE,
            "CATERING.PRODUCT.CREATE",
            "catering.product.create",
            "product",
            "create",
        ),
        (
            CATERING_PRODUCT_READ,
            "CATERING.PRODUCT.READ",
            "catering.product.read",
            "product",
            "read",
        ),
        (
            CATERING_PRODUCT_UPDATE,
            "CATERING.PRODUCT.UPDATE",
            "catering.product.update",
            "product",
            "update",
        ),
        (
            CATERING_PRODUCT_DELETE,
            "CATERING.PRODUCT.DELETE",
            "catering.product.delete",
            "product",
            "delete",
        ),
    ],
)
def test_catering_permission_definition(
    permission,
    code,
    name,
    resource,
    action,
):
    """
    Each Catering permission must expose the expected
    enterprise security metadata.
    """

    assert permission.code == code
    assert permission.name == name
    assert permission.module == "CATERING"
    assert permission.resource == resource
    assert permission.action == action


def test_catering_module_exposes_permissions():
    """
    CateringModule must expose its permissions through
    the enterprise BaseModule contract.
    """

    module = CateringModule()

    assert module.has_permissions()
    assert module.permissions == list(
        CATERING_PERMISSIONS
    )


def test_catering_module_registers_permissions():
    """
    Catering permissions must register through the
    enterprise permission registry.
    """

    permission_registry.clear()

    try:
        module = CateringModule()

        module.register_permissions(None)

        for permission in CATERING_PERMISSIONS:
            assert permission_registry.exists(
                permission.code
            )

            registered = permission_registry.get(
                permission.code
            )

            assert registered is permission

    finally:
        permission_registry.clear()
