"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Integration

Catering Revenue integration provider.
"""

from __future__ import annotations

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.core.integration.providers.base import (
    BaseIntegrationProvider,
)
from app.modules.catering.integration import (
    CateringRevenueContribution,
)
from app.modules.finance.integration.contracts import (
    FINANCE_CATERING_REVENUE_OPERATION,
)
from app.modules.finance.models import (
    FinanceRevenue,
)
from app.modules.finance.services import (
    FinanceRevenueService,
)


class FinanceRevenueIntegrationProvider(
    BaseIntegrationProvider,
):
    """
    Establish the Catering Revenue → Finance provider boundary.

    The provider validates the explicit Catering Revenue contribution
    contract and delegates Finance persistence and idempotency to the
    Finance Revenue service.

    Finance revenue remains in PENDING state after consumption.
    Posting remains a separate Finance lifecycle operation.
    """

    def __init__(
        self,
        revenue_service: FinanceRevenueService | None = None,
    ) -> None:
        """
        Initialize the Finance Revenue integration provider.
        """

        self.revenue_service = (
            revenue_service
            or FinanceRevenueService()
        )

    @property
    def provider_name(self) -> str:
        """Return the enterprise Finance provider name."""

        return "finance"

    def supports(
        self,
        operation: str,
    ) -> bool:
        """Return whether this provider supports the operation."""

        return (
            operation
            == FINANCE_CATERING_REVENUE_OPERATION
        )

    def validate(
        self,
        request: IntegrationRequest,
    ) -> None:
        """
        Validate the enterprise request and Catering Revenue payload.
        """

        super().validate(request)

        if not self.supports(request.operation):
            raise ValueError(
                "Unsupported Finance integration operation."
            )

        if not isinstance(
            request.payload,
            CateringRevenueContribution,
        ):
            raise TypeError(
                "Finance Catering Revenue payload must be "
                "a CateringRevenueContribution."
            )

    def _build_finance_revenue(
        self,
        contribution: CateringRevenueContribution,
    ) -> FinanceRevenue:
        """
        Translate the explicit Catering contribution into
        a Finance-owned Revenue business record.

        contribution_id is the stable business contribution
        identity and becomes Finance's contribution_reference.
        """

        return FinanceRevenue(
            revenue_reference=(
                contribution.revenue_reference
            ),
            contribution_reference=(
                contribution.contribution_id
            ),
            source_type=(
                contribution.source_type
            ),
            source_reference=(
                contribution.source_reference
            ),
            amount=contribution.amount,
            currency=contribution.currency.strip().upper(),
            revenue_date=contribution.revenue_date,
            revenue_classification=(
                contribution.revenue_classification.strip()
                if contribution.revenue_classification
                is not None
                else None
            ),
            status="PENDING",
        )

    def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResponse:
        """
        Consume a Catering Revenue contribution into Finance.

        Finance-side durable idempotency is delegated to
        FinanceRevenueService.consume_contribution().
        """

        try:
            self.validate(request)

            contribution = request.payload

            revenue = self._build_finance_revenue(
                contribution
            )

            consumed = (
                self.revenue_service
                .consume_contribution(
                    revenue
                )
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            return IntegrationResponse(
                success=False,
                message=str(exc),
                error="INVALID_FINANCE_CATERING_REVENUE",
                request_id=request.request_id,
            )

        return IntegrationResponse(
            success=True,
            status_code=200,
            data={
                "finance_revenue_id": consumed.id,
                "revenue_reference": (
                    consumed.revenue_reference
                ),
                "contribution_reference": (
                    consumed.contribution_reference
                ),
                "status": consumed.status,
            },
            message=(
                "Catering Revenue contribution consumed "
                "into Finance."
            ),
            request_id=request.request_id,
        )


__all__ = [
    "FinanceRevenueIntegrationProvider",
]
