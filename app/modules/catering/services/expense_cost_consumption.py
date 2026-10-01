from __future__ import annotations

from datetime import datetime, timezone

from app.modules.catering.integration.contracts import (
    ApprovedExpenseCostContribution,
)
from app.modules.catering.models import CateringExpenseCostAssociation
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)


class CateringExpenseCostConsumptionService:
    """
    Consume an approved Expense contribution for Catering.

    This service owns only the Catering-side consumption state.

    It does not:
    - access or modify Expense records;
    - validate Expense approval;
    - dispatch integrations;
    - calculate or allocate costs;
    - perform accounting or ledger operations.
    """

    def __init__(
        self,
        repository: CateringExpenseCostAssociationRepository | None = None,
    ) -> None:
        self.repository = (
            repository
            if repository is not None
            else CateringExpenseCostAssociationRepository()
        )

    def consume(
        self,
        contribution: ApprovedExpenseCostContribution,
    ) -> CateringExpenseCostAssociation:
        """
        Consume the Catering association identified by the contribution.

        Already-consumed associations are treated as successful idempotent
        retries. Only ELIGIBLE associations may be consumed for the first time.
        """
        association = self.repository.get_by_contribution_id(
            contribution.contribution_id
        )

        if association is None:
            raise ValueError(
                "No eligible Catering Expense Cost Association"
            )

        if association.status == "CONSUMED":
            return association

        if association.status != "ELIGIBLE":
            raise ValueError(
                "Catering Expense Cost Association is not eligible"
            )

        association.mark_consumed(datetime.now(timezone.utc))

        return self.repository.update(association)


__all__ = ["CateringExpenseCostConsumptionService"]
