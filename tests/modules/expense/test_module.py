"""
Tests for the Expense Management business module.
"""

from app.modules.expense.module import ExpenseModule
from app.modules.expense.security import EXPENSE_PERMISSIONS


def test_expense_module_exposes_expected_metadata():
    """
    ExpenseModule exposes the approved enterprise module metadata.
    """

    module = ExpenseModule()
    metadata = module.get_metadata()

    assert metadata.code == "EXPENSE"
    assert metadata.name == "Expense Management"
    assert metadata.version == "1.0.0"
    assert metadata.category == "Business"
    assert metadata.url_prefix == "/expense"
    assert metadata.dependencies == []
    assert metadata.navigation_enabled is True
    assert metadata.dashboard_enabled is False
    assert metadata.active is True


def test_expense_module_exposes_canonical_permissions():
    """
    ExpenseModule exposes the canonical Expense permission aggregate.
    """

    module = ExpenseModule()

    permissions = module.get_permissions()

    assert len(permissions) == len(
        EXPENSE_PERMISSIONS
    )

    assert {
        permission.code
        for permission in permissions
    } == {
        permission.code
        for permission in EXPENSE_PERMISSIONS
    }


def test_expense_module_register_models_imports_domain_models():
    """
    ExpenseModule model registration imports both approved
    Expense Foundation domain models.
    """

    module = ExpenseModule()

    module.register_models(None)

    from app.modules.expense.models import (
        Expense,
        ExpenseClassification,
    )

    assert Expense.__tablename__ == "expenses"
    assert (
        ExpenseClassification.__tablename__
        == "expense_classifications"
    )
