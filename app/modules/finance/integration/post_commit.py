"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance post-commit integration execution.
"""

from __future__ import annotations

from typing import Any

from app.core.execution.context import (
    ExecutionContext,
)
from app.core.execution.post_commit import (
    PostCommitExecutor,
)
from app.core.execution.results import (
    ExecutionResult,
)
from app.core.integration.models import (
    IntegrationRequest,
)
from app.core.integration.service import (
    IntegrationService,
)

from app.modules.catering.commands import (
    RecognizeCateringRevenueCommand,
)
from app.modules.catering.integration.contracts import (
    CateringRevenueContribution,
)
from app.modules.catering.models import (
    CateringRevenue,
)
from app.modules.finance.integration.contracts import (
    FINANCE_CATERING_REVENUE_OPERATION,
    FINANCE_INTEGRATION_PROVIDER,
)


class FinanceCateringRevenuePostCommitExecutor(
    PostCommitExecutor
):
    """
    Deliver recognized Catering Revenue to Finance
    after the originating transaction commits.

    Finance delivery is deliberately post-commit. A delivery
    failure therefore cannot roll back or invalidate the
    already-committed Catering Revenue recognition.
    """

    def __init__(
        self,
        integration_service: IntegrationService | None = None,
    ) -> None:

        self.integration_service = (
            integration_service
            or IntegrationService()
        )

    def execute(
        self,
        command: Any,
        context: Any,
        result: Any,
    ) -> None:
        """
        Deliver a successful Catering Revenue recognition
        to Finance.
        """

        if not isinstance(
            command,
            RecognizeCateringRevenueCommand,
        ):
            return None

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise TypeError(
                "Finance Catering Revenue post-commit "
                "execution requires ExecutionContext."
            )

        if not isinstance(
            result,
            ExecutionResult,
        ):
            raise TypeError(
                "Finance Catering Revenue post-commit "
                "execution requires ExecutionResult."
            )

        if not result.success:
            return None

        revenue = result.data

        if not isinstance(
            revenue,
            CateringRevenue,
        ):
            raise TypeError(
                "Successful Catering Revenue recognition "
                "must return CateringRevenue data."
            )

        contribution = (
            self._build_contribution(
                revenue
            )
        )

        request = IntegrationRequest(
            provider=(
                FINANCE_INTEGRATION_PROVIDER
            ),
            operation=(
                FINANCE_CATERING_REVENUE_OPERATION
            ),
            payload=contribution,
            metadata={
                "source_module": "CATERING",
                "source_operation": context.operation,
                "revenue_id": revenue.id,
                "revenue_reference": (
                    revenue.revenue_reference
                ),
            },
        )

        response = (
            self.integration_service.execute(
                request
            )
        )

        if not response.success:
            raise RuntimeError(
                response.message
                or (
                    "Finance Catering Revenue "
                    "post-commit delivery failed."
                )
            )

        return None

    @staticmethod
    def _build_contribution(
        revenue: CateringRevenue,
    ) -> CateringRevenueContribution:
        """
        Build the frozen Catering Revenue contribution.

        The contribution identity remains stable across retries.
        """

        if not revenue.revenue_reference:
            raise ValueError(
                "Catering Revenue requires a "
                "revenue_reference for Finance delivery."
            )

        if not revenue.source_type:
            raise ValueError(
                "Catering Revenue requires source_type "
                "for Finance delivery."
            )

        if not revenue.source_reference:
            raise ValueError(
                "Catering Revenue requires source_reference "
                "for Finance delivery."
            )

        if revenue.amount is None:
            raise ValueError(
                "Catering Revenue requires an amount "
                "for Finance delivery."
            )

        if not revenue.currency:
            raise ValueError(
                "Catering Revenue requires currency "
                "for Finance delivery."
            )

        if revenue.revenue_date is None:
            raise ValueError(
                "Catering Revenue requires revenue_date "
                "for Finance delivery."
            )

        if revenue.id is None:
            raise ValueError(
                "Catering Revenue requires a persisted "
                "database identity for Finance delivery."
            )

        return CateringRevenueContribution(
            revenue_reference=(
                revenue.revenue_reference
            ),
            source_type=revenue.source_type,
            source_reference=(
                revenue.source_reference
            ),
            amount=revenue.amount,
            currency=revenue.currency,
            revenue_date=revenue.revenue_date,
            revenue_classification=(
                revenue.revenue_classification
            ),
            contribution_id=(
                revenue.revenue_reference
            ),
        )


__all__ = [
    "FinanceCateringRevenuePostCommitExecutor",
]
