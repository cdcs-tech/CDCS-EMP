"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense application services.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.core.data import (
    PaginatedResult,
    QueryOptions,
)
from app.core.workflow.base import WorkflowState

from app.modules.expense.models import Expense
from app.modules.expense.repositories import ExpenseRepository
from app.modules.expense.workflows import (
    APPROVED,
    CLOSED,
    REJECTED,
    RETURNED,
    SUBMITTED,
    ExpenseWorkflow,
)


class ExpenseService(
    CRUDService[Expense],
):
    """
    Application service for Expense records.

    Workflow lifecycle enforcement is performed at the
    service boundary. The Expense workflow owns lifecycle
    transition validity, while this service owns applying
    the resulting state to the entity and persisting the
    business change.
    """

    def __init__(
        self,
        repository: ExpenseRepository | None = None,
        workflow: ExpenseWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository or ExpenseRepository(),
            entity_name="Expense",
        )
        self.workflow = (
            workflow or ExpenseWorkflow()
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[Expense]:
        """
        Return paginated Expense records.
        """
        return self.repository.paginate(options)

    def _transition_workflow(
        self,
        expense: Expense,
        target_state: str,
    ) -> WorkflowState:
        """
        Transition an Expense through its workflow.

        The workflow owns transition validity. This service
        applies the resulting state to the entity but does
        not maintain a second transition matrix.
        """
        state = self.workflow.transition(
            expense.status,
            target_state,
        )

        expense.status = state.name

        return state

    def submit(
        self,
        expense: Expense,
    ) -> Expense:
        """
        Submit an Expense.
        """
        self._transition_workflow(
            expense,
            SUBMITTED,
        )
        return self.update(expense)

    def approve(
        self,
        expense: Expense,
    ) -> Expense:
        """
        Approve an Expense.
        """
        self._transition_workflow(
            expense,
            APPROVED,
        )
        return self.update(expense)

    def reject(
        self,
        expense: Expense,
    ) -> Expense:
        """
        Reject an Expense.
        """
        self._transition_workflow(
            expense,
            REJECTED,
        )
        return self.update(expense)

    def return_expense(
        self,
        expense: Expense,
    ) -> Expense:
        """
        Return an Expense for correction.
        """
        self._transition_workflow(
            expense,
            RETURNED,
        )
        return self.update(expense)

    def resubmit(
        self,
        expense: Expense,
    ) -> Expense:
        """
        Resubmit a returned Expense.
        """
        self._transition_workflow(
            expense,
            SUBMITTED,
        )
        return self.update(expense)

    def close(
        self,
        expense: Expense,
    ) -> Expense:
        """
        Close an approved Expense.
        """
        self._transition_workflow(
            expense,
            CLOSED,
        )
        return self.update(expense)
