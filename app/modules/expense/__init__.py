"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Business Module

Public API.
"""

from app.modules.expense.module import (
    ExpenseModule,
)

from app.modules.expense.manifest import (
    MODULE_MANIFEST,
)


__all__ = [
    "ExpenseModule",
    "MODULE_MANIFEST",
]
