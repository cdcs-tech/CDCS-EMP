"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense workflows.
"""

from app.modules.expense.workflows.expense import (
    ACTION_APPROVE,
    ACTION_CLOSE,
    ACTION_REJECT,
    ACTION_RESUBMIT,
    ACTION_RETURN,
    ACTION_SUBMIT,
    APPROVED,
    CLOSED,
    DRAFT,
    ExpenseWorkflow,
    REJECTED,
    RETURNED,
    SUBMITTED,
)


__all__ = [
    "ExpenseWorkflow",
    "DRAFT",
    "SUBMITTED",
    "RETURNED",
    "APPROVED",
    "REJECTED",
    "CLOSED",
    "ACTION_SUBMIT",
    "ACTION_APPROVE",
    "ACTION_REJECT",
    "ACTION_RETURN",
    "ACTION_RESUBMIT",
    "ACTION_CLOSE",
]
