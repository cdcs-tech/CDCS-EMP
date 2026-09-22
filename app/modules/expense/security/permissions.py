"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense permission definitions.
"""

from app.core.security import Permission


# ---------------------------------------------------------------------------
# Expense Classification Permissions
# ---------------------------------------------------------------------------

EXPENSE_CLASSIFICATION_CREATE = Permission(
    code="EXPENSE.EXPENSE_CLASSIFICATION.CREATE",
    name="expense.expense_classification.create",
    description="Create Expense Management classifications.",
    module="EXPENSE",
    resource="expense_classification",
    action="create",
)

EXPENSE_CLASSIFICATION_READ = Permission(
    code="EXPENSE.EXPENSE_CLASSIFICATION.READ",
    name="expense.expense_classification.read",
    description="Read Expense Management classifications.",
    module="EXPENSE",
    resource="expense_classification",
    action="read",
)

EXPENSE_CLASSIFICATION_UPDATE = Permission(
    code="EXPENSE.EXPENSE_CLASSIFICATION.UPDATE",
    name="expense.expense_classification.update",
    description="Update Expense Management classifications.",
    module="EXPENSE",
    resource="expense_classification",
    action="update",
)

EXPENSE_CLASSIFICATION_DELETE = Permission(
    code="EXPENSE.EXPENSE_CLASSIFICATION.DELETE",
    name="expense.expense_classification.delete",
    description="Delete Expense Management classifications.",
    module="EXPENSE",
    resource="expense_classification",
    action="delete",
)


# ---------------------------------------------------------------------------
# Expense Permissions
# ---------------------------------------------------------------------------

EXPENSE_CREATE = Permission(
    code="EXPENSE.EXPENSE.CREATE",
    name="expense.expense.create",
    description="Create Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="create",
)

EXPENSE_READ = Permission(
    code="EXPENSE.EXPENSE.READ",
    name="expense.expense.read",
    description="Read Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="read",
)

EXPENSE_UPDATE = Permission(
    code="EXPENSE.EXPENSE.UPDATE",
    name="expense.expense.update",
    description="Update Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="update",
)

EXPENSE_DELETE = Permission(
    code="EXPENSE.EXPENSE.DELETE",
    name="expense.expense.delete",
    description="Delete Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="delete",
)


# ---------------------------------------------------------------------------
# Aggregate Expense Permissions
# ---------------------------------------------------------------------------

EXPENSE_PERMISSIONS = (
    EXPENSE_CLASSIFICATION_CREATE,
    EXPENSE_CLASSIFICATION_READ,
    EXPENSE_CLASSIFICATION_UPDATE,
    EXPENSE_CLASSIFICATION_DELETE,
    EXPENSE_CREATE,
    EXPENSE_READ,
    EXPENSE_UPDATE,
    EXPENSE_DELETE,
)


__all__ = [
    "EXPENSE_CLASSIFICATION_CREATE",
    "EXPENSE_CLASSIFICATION_READ",
    "EXPENSE_CLASSIFICATION_UPDATE",
    "EXPENSE_CLASSIFICATION_DELETE",
    "EXPENSE_CREATE",
    "EXPENSE_READ",
    "EXPENSE_UPDATE",
    "EXPENSE_DELETE",
    "EXPENSE_PERMISSIONS",
]
