"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Finance Revenue application service.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.core.crud.transaction import (
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.workflow import WorkflowState
from app.modules.finance.models import (
    FinanceRevenue,
)
from app.modules.finance.repositories import (
    FinanceRevenueRepository,
)
from app.modules.finance.workflows import (
    FinanceRevenueWorkflow,
)


class FinanceRevenueService(
    CRUDService[FinanceRevenue],
):
    """
    Application service for Finance Revenue.

    Owns Finance Revenue business operations while
    delegating persistence to the repository and
    lifecycle transitions to the workflow.
    """

    def __init__(
        self,
        repository: FinanceRevenueRepository | None = None,
        workflow: FinanceRevenueWorkflow | None = None,
        transaction_manager: TransactionManager | None = None,
    ) -> None:
        super().__init__(
            repository or FinanceRevenueRepository(),
            entity_name="Finance Revenue",
        )

        self.workflow = (
            workflow or FinanceRevenueWorkflow()
        )

        self.transaction_manager = (
            transaction_manager
            or SQLAlchemyTransactionManager()
        )

    def _transition_workflow(
        self,
        revenue: FinanceRevenue,
        target_state: str,
    ) -> WorkflowState:
        """
        Transition a Finance Revenue record through
        its registered workflow.
        """

        state = self.workflow.transition(
            revenue.status,
            target_state,
        )

        revenue.status = state.name

        return state

    def consume_contribution(
        self,
        revenue: FinanceRevenue,
    ) -> FinanceRevenue:
        """
        Consume a business revenue contribution into Finance.

        The contribution_reference is the stable Finance-side
        idempotency identity.

        A previously consumed contribution returns the
        existing Finance Revenue record without creating a
        duplicate.

        A newly consumed contribution is persisted as a
        Finance Revenue record in PENDING state.

        Finance lifecycle posting remains a separate operation.
        """

        if revenue is None:
            raise ValueError(
                "Finance Revenue contribution is required."
            )

        if not isinstance(
            revenue.contribution_reference,
            str,
        ):
            raise ValueError(
                "Finance Revenue contribution reference is required."
            )

        contribution_reference = (
            revenue.contribution_reference.strip()
        )

        if not contribution_reference:
            raise ValueError(
                "Finance Revenue contribution reference is required."
            )

        revenue.contribution_reference = (
            contribution_reference
        )

        with self.transaction_manager.transaction():
            existing = (
                self.repository
                .get_by_contribution_reference(
                    contribution_reference
                )
            )

            if existing is not None:
                return existing

            revenue.status = (
                FinanceRevenueWorkflow.PENDING
            )

            return self.repository.add(
                revenue
            )

    def post(
        self,
        revenue: FinanceRevenue,
    ) -> FinanceRevenue:
        """
        Post a pending Finance Revenue record.
        """

        self._transition_workflow(
            revenue,
            FinanceRevenueWorkflow.POSTED,
        )

        return self.update(
            revenue
        )


__all__ = [
    "FinanceRevenueService",
]
