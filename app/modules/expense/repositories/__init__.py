"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Repository package.
"""

from app.modules.expense.repositories.expense import (
    ExpenseRepository,
)

from app.modules.expense.repositories.expense_classification import (
    ExpenseClassificationRepository,
)


__all__ = [
    "ExpenseRepository",
    "ExpenseClassificationRepository",
]
