"""
Tests for Expense Management permission definitions.
"""

from app.modules.expense.security.permissions import (
    EXPENSE_PERMISSIONS,
)


EXPECTED_PERMISSION_MATRIX = {
    "EXPENSE.EXPENSE_CLASSIFICATION.CREATE": (
        "expense_classification",
        "create",
    ),
    "EXPENSE.EXPENSE_CLASSIFICATION.READ": (
        "expense_classification",
        "read",
    ),
    "EXPENSE.EXPENSE_CLASSIFICATION.UPDATE": (
        "expense_classification",
        "update",
    ),
    "EXPENSE.EXPENSE_CLASSIFICATION.DELETE": (
        "expense_classification",
        "delete",
    ),
    "EXPENSE.EXPENSE.CREATE": (
        "expense",
        "create",
    ),
    "EXPENSE.EXPENSE.READ": (
        "expense",
        "read",
    ),
    "EXPENSE.EXPENSE.UPDATE": (
        "expense",
        "update",
    ),
    "EXPENSE.EXPENSE.DELETE": (
        "expense",
        "delete",
    ),
}


def test_expense_permissions_have_expected_count():
    """
    Expense Management exposes the complete expected permission set.
    """

    assert len(EXPENSE_PERMISSIONS) == 8


def test_expense_permission_codes_are_unique():
    """
    Expense Management permission codes are unique.
    """

    codes = [
        permission.code
        for permission in EXPENSE_PERMISSIONS
    ]

    assert len(codes) == len(set(codes))


def test_expense_permissions_match_expected_matrix():
    """
    Every Expense Management permission has the expected
    resource and action.
    """

    actual_codes = {
        permission.code
        for permission in EXPENSE_PERMISSIONS
    }

    assert actual_codes == set(
        EXPECTED_PERMISSION_MATRIX
    )

    for permission in EXPENSE_PERMISSIONS:
        expected_resource, expected_action = (
            EXPECTED_PERMISSION_MATRIX[
                permission.code
            ]
        )

        assert permission.module == "EXPENSE"
        assert permission.resource == expected_resource
        assert permission.action == expected_action


def test_expense_permission_names_are_human_readable():
    """
    Expense Management permissions expose non-empty display names.
    """

    assert all(
        permission.name.strip()
        for permission in EXPENSE_PERMISSIONS
    )


def test_expense_permission_codes_follow_enterprise_convention():
    """
    Expense Management permission codes follow the canonical
    module.resource.action convention.
    """

    for permission in EXPENSE_PERMISSIONS:
        expected_code = (
            f"EXPENSE."
            f"{permission.resource.upper()}."
            f"{permission.action.upper()}"
        )

        assert permission.code == expected_code
