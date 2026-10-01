"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense integration boundaries.
"""

from app.modules.expense.integration.post_commit import (
    ExpenseCateringPostCommitExecutor,
)

__all__ = [
    "ExpenseCateringPostCommitExecutor",
]
