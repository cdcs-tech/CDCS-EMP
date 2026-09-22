"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module Manifest
"""

from app.core.discovery import ModuleManifest

from app.modules.expense.module import (
    ExpenseModule,
)


MODULE_MANIFEST = ModuleManifest(
    name="Expense Management",
    code="EXPENSE",
    module_class=ExpenseModule,
    version="1.0.0",
    description=(
        "Reusable operational expense management capability."
    ),
    author="CDCS",
    dependencies=[],
    enabled=True,
)


__all__ = [
    "MODULE_MANIFEST",
]
