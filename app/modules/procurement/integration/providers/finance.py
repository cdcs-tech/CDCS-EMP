"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Finance Integration

Finance integration provider boundary.
"""

from __future__ import annotations

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.core.integration.providers.base import (
    BaseIntegrationProvider,
)
from app.modules.procurement.integration import (
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
    ProcurementFinancialEffectRequest,
)


class FinanceProcurementIntegrationProvider(
    BaseIntegrationProvider,
):
    """
    Establish the Procurement-to-Finance integration provider boundary.

    This Stage 1 provider validates Procurement-owned financial-effect
    requests against the enterprise Integration Framework contract.

    Finance processing is intentionally not implemented at this stage.
    Financial treatment, persistence, accounting, invoices, payments,
    settlement, ledger processing, retry infrastructure, and Finance
    workflow remain outside this provider boundary.
    """

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
            == FINANCE_PROCUREMENT_COMMITMENT_OPERATION
        )

    def validate(
        self,
        request: IntegrationRequest,
    ) -> None:
        """
        Validate the enterprise request and Procurement-owned payload.
        """

        super().validate(request)

        if not self.supports(request.operation):
            raise ValueError(
                "Unsupported Finance integration operation."
            )

        if not isinstance(
            request.payload,
            ProcurementFinancialEffectRequest,
        ):
            raise TypeError(
                "Finance procurement commitment payload must be "
                "a ProcurementFinancialEffectRequest."
            )

    def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResponse:
        """
        Validate the Finance integration boundary.

        Finance processing is intentionally deferred until the future
        Finance capability is implemented.
        """

        try:
            self.validate(request)
        except (
            TypeError,
            ValueError,
        ) as exc:
            return IntegrationResponse(
                success=False,
                message=str(exc),
                error="INVALID_FINANCE_PROCUREMENT_COMMITMENT",
                request_id=request.request_id,
            )

        return IntegrationResponse(
            success=False,
            message=(
                "Finance procurement commitment processing is "
                "not implemented."
            ),
            error="FINANCE_PROCESSING_NOT_IMPLEMENTED",
            request_id=request.request_id,
        )
