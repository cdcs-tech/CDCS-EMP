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
# Expense CRUD Permissions
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
# Expense Workflow Permissions
# ---------------------------------------------------------------------------

EXPENSE_SUBMIT = Permission(
    code="EXPENSE.EXPENSE.SUBMIT",
    name="expense.expense.submit",
    description="Submit Expense Management expense records for approval.",
    module="EXPENSE",
    resource="expense",
    action="submit",
)

EXPENSE_APPROVE = Permission(
    code="EXPENSE.EXPENSE.APPROVE",
    name="expense.expense.approve",
    description="Approve submitted Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="approve",
)

EXPENSE_REJECT = Permission(
    code="EXPENSE.EXPENSE.REJECT",
    name="expense.expense.reject",
    description="Reject submitted Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="reject",
)

EXPENSE_RETURN = Permission(
    code="EXPENSE.EXPENSE.RETURN",
    name="expense.expense.return",
    description="Return submitted Expense Management expense records for correction.",
    module="EXPENSE",
    resource="expense",
    action="return",
)

EXPENSE_RESUBMIT = Permission(
    code="EXPENSE.EXPENSE.RESUBMIT",
    name="expense.expense.resubmit",
    description="Resubmit returned Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="resubmit",
)

EXPENSE_CLOSE = Permission(
    code="EXPENSE.EXPENSE.CLOSE",
    name="expense.expense.close",
    description="Close approved Expense Management expense records.",
    module="EXPENSE",
    resource="expense",
    action="close",
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
    EXPENSE_SUBMIT,
    EXPENSE_APPROVE,
    EXPENSE_REJECT,
    EXPENSE_RETURN,
    EXPENSE_RESUBMIT,
    EXPENSE_CLOSE,
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
    "EXPENSE_SUBMIT",
    "EXPENSE_APPROVE",
    "EXPENSE_REJECT",
    "EXPENSE_RETURN",
    "EXPENSE_RESUBMIT",
    "EXPENSE_CLOSE",
    "EXPENSE_PERMISSIONS",
]
