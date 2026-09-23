"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense workflow definition.
"""

from __future__ import annotations

from app.core.workflow.base import (
    BaseWorkflow,
    WorkflowState,
    WorkflowTransition,
)


DRAFT = "DRAFT"
SUBMITTED = "SUBMITTED"
RETURNED = "RETURNED"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
CLOSED = "CLOSED"


ACTION_SUBMIT = "SUBMIT"
ACTION_APPROVE = "APPROVE"
ACTION_REJECT = "REJECT"
ACTION_RETURN = "RETURN"
ACTION_RESUBMIT = "RESUBMIT"
ACTION_CLOSE = "CLOSE"


class ExpenseWorkflow(BaseWorkflow):
    """
    Defines the governed lifecycle for Expense entities.

    Workflow validity is limited to state and transition rules.
    Authorization, execution, persistence, transactions, audit,
    events, and integrations remain outside this workflow.
    """

    def __init__(self) -> None:
        super().__init__()

        self.add_state(
            WorkflowState(
                name=DRAFT,
                description=(
                    "Expense is being prepared or corrected."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=SUBMITTED,
                description=(
                    "Expense has been submitted for operational review."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=RETURNED,
                description=(
                    "Expense has been returned for correction "
                    "or additional information."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=APPROVED,
                description=(
                    "Expense has received operational approval."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=REJECTED,
                description=(
                    "Expense has been operationally rejected."
                ),
            )
        )

        self.add_state(
            WorkflowState(
                name=CLOSED,
                description=(
                    "Expense operational lifecycle is complete."
                ),
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=DRAFT,
                target=SUBMITTED,
                action=ACTION_SUBMIT,
                metadata={
                    "operation": "expense.submit",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=SUBMITTED,
                target=APPROVED,
                action=ACTION_APPROVE,
                metadata={
                    "operation": "expense.approve",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=SUBMITTED,
                target=REJECTED,
                action=ACTION_REJECT,
                metadata={
                    "operation": "expense.reject",
                    "terminal": True,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=SUBMITTED,
                target=RETURNED,
                action=ACTION_RETURN,
                metadata={
                    "operation": "expense.return",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=RETURNED,
                target=SUBMITTED,
                action=ACTION_RESUBMIT,
                metadata={
                    "operation": "expense.resubmit",
                    "terminal": False,
                },
            )
        )

        self.add_transition(
            WorkflowTransition(
                source=APPROVED,
                target=CLOSED,
                action=ACTION_CLOSE,
                metadata={
                    "operation": "expense.close",
                    "terminal": True,
                },
            )
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
