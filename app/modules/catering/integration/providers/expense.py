"""Catering approved Expense integration provider."""

from __future__ import annotations

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.core.integration.providers.base import (
    BaseIntegrationProvider,
)
from app.modules.catering.integration import (
    CATERING_CONSUME_APPROVED_EXPENSE_OPERATION,
    CATERING_INTEGRATION_PROVIDER,
    ApprovedExpenseCostContribution,
)
from app.modules.catering.services import (
    CateringExpenseCostConsumptionService,
)


class CateringExpenseIntegrationProvider(
    BaseIntegrationProvider,
):
    """
    Consume approved Expense contributions at the Catering boundary.

    The provider validates the enterprise integration request and delegates
    Catering-side consumption to CateringExpenseCostConsumptionService.

    It does not access Expense records, perform approval validation, calculate
    costs, allocate expenses, or perform accounting.
    """

    def __init__(
        self,
        consumption_service: CateringExpenseCostConsumptionService | None = None,
    ) -> None:
        self.consumption_service = (
            consumption_service
            if consumption_service is not None
            else CateringExpenseCostConsumptionService()
        )

    @property
    def provider_name(self) -> str:
        """Return the enterprise Catering provider name."""

        return CATERING_INTEGRATION_PROVIDER

    def supports(
        self,
        operation: str,
    ) -> bool:
        """Return whether this provider supports the operation."""

        return (
            operation
            == CATERING_CONSUME_APPROVED_EXPENSE_OPERATION
        )

    def validate(
        self,
        request: IntegrationRequest,
    ) -> None:
        """Validate the enterprise request and Catering payload."""

        super().validate(request)

        if not self.supports(request.operation):
            raise ValueError(
                "Unsupported Catering integration operation."
            )

        if not isinstance(
            request.payload,
            ApprovedExpenseCostContribution,
        ):
            raise TypeError(
                "Catering approved Expense contribution payload must be "
                "an ApprovedExpenseCostContribution."
            )

    def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResponse:
        """
        Consume an approved Expense contribution for Catering.

        Validation failures and Catering consumption failures are translated
        into normalized integration responses.
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
                error="INVALID_CATERING_EXPENSE_CONTRIBUTION",
                request_id=request.request_id,
            )

        try:
            association = self.consumption_service.consume(
                request.payload
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            return IntegrationResponse(
                success=False,
                message=str(exc),
                error="CATERING_EXPENSE_CONSUMPTION_FAILED",
                request_id=request.request_id,
            )

        return IntegrationResponse(
            success=True,
            data=association,
            message=(
                "Approved Expense contribution consumed by Catering."
            ),
            request_id=request.request_id,
        )


__all__ = ["CateringExpenseIntegrationProvider"]
