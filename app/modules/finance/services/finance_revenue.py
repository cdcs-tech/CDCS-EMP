"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Finance Revenue application service.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.core.workflow.base import WorkflowState

from app.modules.finance.models import FinanceRevenue
from app.modules.finance.repositories import FinanceRevenueRepository
from app.modules.finance.workflows import FinanceRevenueWorkflow


class FinanceRevenueService(
    CRUDService[FinanceRevenue],
):
    """
    Application service for Finance Revenue records.

    Workflow lifecycle enforcement is performed at the
    service boundary. The Finance Revenue workflow owns
    transition validity, while this service applies the
    resulting state and persists the business change.
    """

    def __init__(
        self,
        repository: FinanceRevenueRepository | None = None,
        workflow: FinanceRevenueWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository or FinanceRevenueRepository(),
            entity_name="Finance Revenue",
        )
        self.workflow = (
            workflow or FinanceRevenueWorkflow()
        )

    def _transition_workflow(
        self,
        revenue: FinanceRevenue,
        target_state: str,
    ) -> WorkflowState:
        """
        Transition a Finance Revenue record through its workflow.

        The workflow owns transition validity. This service
        applies the resulting state to the entity but does
        not maintain a second transition matrix.
        """
        state = self.workflow.transition(
            revenue.status,
            target_state,
        )

        revenue.status = state.name

        return state

    def post(
        self,
        revenue: FinanceRevenue,
    ) -> FinanceRevenue:
        """
        Post a Finance Revenue record.
        """
        self._transition_workflow(
            revenue,
            FinanceRevenueWorkflow.POSTED,
        )

        return self.update(revenue)


__all__ = [
    "FinanceRevenueService",
]
