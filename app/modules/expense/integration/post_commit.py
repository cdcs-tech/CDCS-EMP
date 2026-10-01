"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense → Catering post-commit integration.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.core.execution.context import ExecutionContext
from app.core.execution.post_commit import PostCommitExecutor
from app.core.execution.results import ExecutionResult
from app.core.integration import (
    IntegrationRequest,
    IntegrationService,
    integration_service as default_integration_service,
)

from app.modules.catering.integration import (
    CATERING_CONSUME_APPROVED_EXPENSE_OPERATION,
    CATERING_INTEGRATION_PROVIDER,
    ApprovedExpenseCostContribution,
)
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.expense.commands import (
    ApproveExpenseCommand,
)
from app.modules.expense.models import Expense


class ExpenseCateringPostCommitExecutor(
    PostCommitExecutor,
):
    """
    Deliver approved Expense facts to Catering after
    the originating Expense transaction has committed.

    The executor owns only post-commit delivery orchestration.

    It does not:
    - approve or otherwise modify Expense records;
    - create or modify Catering associations;
    - mark Catering associations as consumed;
    - calculate or allocate costs;
    - perform accounting or ledger operations.

    Catering remains responsible for consuming the delivered
    contribution and maintaining its own consumption state.
    """

    def __init__(
        self,
        association_repository: (
            CateringExpenseCostAssociationRepository | None
        ) = None,
        integration_service: (
            IntegrationService | None
        ) = None,
    ) -> None:
        self.association_repository = (
            association_repository
            or CateringExpenseCostAssociationRepository()
        )

        self.integration_service = (
            integration_service
            or default_integration_service
        )

        if not isinstance(
            self.association_repository,
            CateringExpenseCostAssociationRepository,
        ):
            raise TypeError(
                "association_repository must be a "
                "CateringExpenseCostAssociationRepository."
            )

        if not isinstance(
            self.integration_service,
            IntegrationService,
        ):
            raise TypeError(
                "integration_service must be an "
                "IntegrationService."
            )

    def execute(
        self,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Deliver all eligible Catering Expense contributions
        after successful Expense approval commit.

        Non-approval commands and unsuccessful approval results
        are ignored.

        Each eligible Catering association is delivered
        independently so one failed association does not prevent
        other eligible associations from being attempted.

        Integration failures are re-raised after all eligible
        associations have been attempted. CommandDispatcher
        isolates those post-commit failures from the already
        committed Expense transaction.
        """

        if not isinstance(
            command,
            ApproveExpenseCommand,
        ):
            return

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise TypeError(
                "context must be an ExecutionContext."
            )

        if not isinstance(
            result,
            ExecutionResult,
        ):
            raise TypeError(
                "result must be an ExecutionResult."
            )

        if not result.is_success():
            return

        expense = result.data

        if not isinstance(
            expense,
            Expense,
        ):
            raise TypeError(
                "Successful Expense approval result "
                "must contain an Expense."
            )

        approved_at = self._approved_at(
            result
        )

        associations = (
            self.association_repository.get_eligible_by_expense_id(
                expense.id
            )
        )

        first_failure: Exception | None = None

        for association in associations:
            try:
                contribution = (
                    self._build_contribution(
                        expense=expense,
                        association=association,
                        approved_at=approved_at,
                    )
                )

                request = IntegrationRequest(
                    provider=CATERING_INTEGRATION_PROVIDER,
                    operation=(
                        CATERING_CONSUME_APPROVED_EXPENSE_OPERATION
                    ),
                    payload=contribution,
                    metadata={
                        "expense_id": expense.id,
                        "catering_context_type": (
                            association.catering_context_type
                        ),
                        "catering_context_reference": (
                            association.catering_context_reference
                        ),
                    },
                )

                integration_result = (
                    self.integration_service.execute(
                        request
                    )
                )

                if not integration_result.success:
                    raise RuntimeError(
                        "Catering approved Expense contribution "
                        "delivery failed."
                    )

            except Exception as exc:
                if first_failure is None:
                    first_failure = exc

        if first_failure is not None:
            raise first_failure

    @staticmethod
    def _approved_at(
        result: ExecutionResult,
    ) -> datetime:
        """
        Retrieve the approval timestamp captured by the
        Expense approval handler.
        """

        metadata = result.metadata or {}

        approved_at = metadata.get(
            "approved_at"
        )

        if not isinstance(
            approved_at,
            datetime,
        ):
            raise ValueError(
                "Expense approval result does not contain "
                "a valid approved_at timestamp."
            )

        return approved_at

    @staticmethod
    def _build_contribution(
        *,
        expense: Expense,
        association: Any,
        approved_at: datetime,
    ) -> ApprovedExpenseCostContribution:
        """
        Build the immutable Expense business fact delivered
        across the enterprise integration boundary.
        """

        classification = expense.classification

        if classification is None:
            raise ValueError(
                "Approved Expense does not have a valid "
                "Expense classification."
            )

        classification_reference = (
            classification.code
        )

        if not classification_reference:
            raise ValueError(
                "Expense classification does not have a "
                "valid classification code."
            )

        return ApprovedExpenseCostContribution(
            expense_id=expense.id,
            description=expense.description,
            amount=expense.amount,
            expense_date=expense.expense_date,
            classification_reference=(
                classification_reference
            ),
            catering_context_type=(
                association.catering_context_type
            ),
            catering_context_reference=(
                association.catering_context_reference
            ),
            approved_at=approved_at,
            contribution_id=association.contribution_id,
        )


__all__ = [
    "ExpenseCateringPostCommitExecutor",
]
