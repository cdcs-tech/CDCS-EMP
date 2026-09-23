"""
Tests for Catering permission definitions.
"""

from app.modules.catering.module import (
    CateringModule,
)

from app.modules.catering.security.permissions import (
    CATERING_PERMISSIONS,
)


EXPECTED_PERMISSION_MATRIX = {
    "CATERING.PRODUCT_CATEGORY.CREATE": (
        "product_category",
        "create",
    ),
    "CATERING.PRODUCT_CATEGORY.READ": (
        "product_category",
        "read",
    ),
    "CATERING.PRODUCT_CATEGORY.UPDATE": (
        "product_category",
        "update",
    ),
    "CATERING.PRODUCT_CATEGORY.DELETE": (
        "product_category",
        "delete",
    ),
    "CATERING.PRODUCT.CREATE": (
        "product",
        "create",
    ),
    "CATERING.PRODUCT.READ": (
        "product",
        "read",
    ),
    "CATERING.PRODUCT.UPDATE": (
        "product",
        "update",
    ),
    "CATERING.PRODUCT.DELETE": (
        "product",
        "delete",
    ),
    "CATERING.STOCK_ITEM.CREATE": (
        "stock_item",
        "create",
    ),
    "CATERING.STOCK_ITEM.READ": (
        "stock_item",
        "read",
    ),
    "CATERING.STOCK_ITEM.UPDATE": (
        "stock_item",
        "update",
    ),
    "CATERING.STOCK_ITEM.DELETE": (
        "stock_item",
        "delete",
    ),
    "CATERING.INVENTORY_LOCATION.CREATE": (
        "inventory_location",
        "create",
    ),
    "CATERING.INVENTORY_LOCATION.READ": (
        "inventory_location",
        "read",
    ),
    "CATERING.INVENTORY_LOCATION.UPDATE": (
        "inventory_location",
        "update",
    ),
    "CATERING.INVENTORY_LOCATION.DELETE": (
        "inventory_location",
        "delete",
    ),
    "CATERING.STOCK_BALANCE.READ": (
        "stock_balance",
        "read",
    ),
    "CATERING.STOCK_MOVEMENT.CREATE": (
        "stock_movement",
        "create",
    ),
    "CATERING.STOCK_MOVEMENT.READ": (
        "stock_movement",
        "read",
    ),
    "CATERING.STOCK_MOVEMENT.POST": (
        "stock_movement",
        "post",
    ),
    "CATERING.STOCK_TRANSFER.CREATE": (
        "stock_transfer",
        "create",
    ),
    "CATERING.STOCK_TRANSFER.READ": (
        "stock_transfer",
        "read",
    ),
    "CATERING.STOCK_TRANSFER.POST": (
        "stock_transfer",
        "post",
    ),
}


def test_catering_permissions_have_expected_count():
    """
    Catering exposes the complete expected permission set.
    """

    assert len(CATERING_PERMISSIONS) == 23


def test_catering_permission_codes_are_unique():
    """
    Catering permission codes are unique.
    """

    codes = [
        permission.code
        for permission in CATERING_PERMISSIONS
    ]

    assert len(codes) == len(set(codes))


def test_catering_permissions_match_expected_matrix():
    """
    Every Catering permission has the expected resource and action.
    """

    actual_codes = {
        permission.code
        for permission in CATERING_PERMISSIONS
    }

    assert actual_codes == set(
        EXPECTED_PERMISSION_MATRIX
    )

    for permission in CATERING_PERMISSIONS:

        expected_resource, expected_action = (
            EXPECTED_PERMISSION_MATRIX[
                permission.code
            ]
        )

        assert permission.module == "CATERING"
        assert permission.resource == expected_resource
        assert permission.action == expected_action


def test_catering_inventory_permissions_include_operational_post_actions():
    """
    Inventory movement and transfer posting are explicitly
    represented as operational permissions.
    """

    permissions = {
        permission.code: permission
        for permission in CATERING_PERMISSIONS
    }

    assert permissions[
        "CATERING.STOCK_MOVEMENT.POST"
    ].resource == "stock_movement"

    assert permissions[
        "CATERING.STOCK_MOVEMENT.POST"
    ].action == "post"

    assert permissions[
        "CATERING.STOCK_TRANSFER.POST"
    ].resource == "stock_transfer"

    assert permissions[
        "CATERING.STOCK_TRANSFER.POST"
    ].action == "post"


def test_catering_stock_balance_is_read_only():
    """
    Stock balance is exposed as a read-only operational resource.
    """

    stock_balance_permissions = [
        permission
        for permission in CATERING_PERMISSIONS
        if permission.resource == "stock_balance"
    ]

    assert len(
        stock_balance_permissions
    ) == 1

    assert stock_balance_permissions[
        0
    ].action == "read"


def test_catering_inventory_permission_names_are_human_readable():
    """
    Inventory permissions expose non-empty display names.
    """

    inventory_resources = {
        "stock_item",
        "inventory_location",
        "stock_balance",
        "stock_movement",
        "stock_transfer",
    }

    inventory_permissions = [
        permission
        for permission in CATERING_PERMISSIONS
        if permission.resource in inventory_resources
    ]

    assert len(
        inventory_permissions
    ) == 15

    assert all(
        permission.name.strip()
        for permission in inventory_permissions
    )


def test_catering_module_exposes_same_permission_set():
    """
    CateringModule exposes the canonical Catering permission
    aggregate through its module lifecycle contract.
    """

    permissions = CateringModule().get_permissions()

    assert len(permissions) == len(
        CATERING_PERMISSIONS
    )

    assert {
        permission.code
        for permission in permissions
    } == {
        permission.code
        for permission in CATERING_PERMISSIONS
    }


def test_catering_inventory_permission_codes_follow_enterprise_convention():
    """
    Inventory permission codes follow the canonical
    module.resource.action convention.
    """

    inventory_permissions = [
        permission
        for permission in CATERING_PERMISSIONS
        if permission.resource in {
            "stock_item",
            "inventory_location",
            "stock_balance",
            "stock_movement",
            "stock_transfer",
        }
    ]

    for permission in inventory_permissions:

        expected_code = (
            f"CATERING."
            f"{permission.resource.upper()}."
            f"{permission.action.upper()}"
        )

        assert permission.code == expected_code
