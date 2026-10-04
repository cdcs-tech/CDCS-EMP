"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Read-side event profitability composition service.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)
from app.modules.catering.repositories.catering_revenue import (
    CateringRevenueRepository,
)
from app.modules.catering.repositories.expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.expense.repositories.expense import (
    ExpenseRepository,
)


CATERING_EVENT_CONTEXT_TYPE = "CATERING_EVENT"


@dataclass(frozen=True)
class EventProfitabilityCostContribution:
    """
    Read-only representation of one consumed Catering cost contribution.
    """

    association_id: int
    contribution_id: str
    expense_id: int
    expense_amount: Decimal


@dataclass(frozen=True)
class EventProfitabilityResult:
    """
    Read-only profitability result composed from authoritative module data.

    The result is not a persisted domain entity and does not establish
    ownership of revenue or Expense data inside the profitability service.
    """

    event_id: int
    event_reference: str
    revenue_reference: str
    revenue_amount: Decimal
    currency: str
    cost_contributions: tuple[
        EventProfitabilityCostContribution,
        ...,
    ]
    total_cost: Decimal
    profit: Decimal


class EventProfitabilityService:
    """
    Compose profitability for one Catering Event.

    The service is deliberately read-only:

    - Catering Event remains owned by Catering.
    - Catering Revenue remains owned by Catering.
    - Expense remains owned by Expense.
    - Catering Expense Cost Association remains the Catering-side
      contribution/consumption relationship.
    - No profitability result is persisted.
    """

    def __init__(
        self,
        *,
        catering_event_repository: CateringEventRepository,
        catering_revenue_repository: CateringRevenueRepository,
        expense_cost_association_repository: (
            CateringExpenseCostAssociationRepository
        ),
        expense_repository: ExpenseRepository,
    ) -> None:
        self._catering_event_repository = (
            catering_event_repository
        )
        self._catering_revenue_repository = (
            catering_revenue_repository
        )
        self._expense_cost_association_repository = (
            expense_cost_association_repository
        )
        self._expense_repository = expense_repository

    def calculate_for_event(
        self,
        event_id: int,
    ) -> EventProfitabilityResult:
        """
        Calculate read-only profitability for one Catering Event.

        Only recognized Catering Revenue is included.

        Only consumed Catering Expense Cost Associations for the
        Event are included.

        The authoritative cost amount is read from Expense.amount.
        """

        event = self._catering_event_repository.get_by_id(
            event_id
        )

        if event is None:
            raise ValueError(
                f"Catering Event not found: {event_id}"
            )

        revenue = (
            self._catering_revenue_repository
            .get_recognized_by_event_id(event.id)
        )

        if revenue is None:
            raise ValueError(
                "Recognized Catering Revenue not found for "
                f"event: {event.id}"
            )

        event_reference = f"EVENT-{event.id}"

        associations = (
            self._expense_cost_association_repository
            .get_consumed_by_catering_context(
                CATERING_EVENT_CONTEXT_TYPE,
                event_reference,
            )
        )

        contributions: list[
            EventProfitabilityCostContribution
        ] = []

        for association in associations:
            expense = self._expense_repository.get_by_id(
                association.expense_id
            )

            if expense is None:
                raise ValueError(
                    "Expense not found for Catering cost "
                    f"association: {association.id}"
                )

            contributions.append(
                EventProfitabilityCostContribution(
                    association_id=association.id,
                    contribution_id=association.contribution_id,
                    expense_id=expense.id,
                    expense_amount=Decimal(expense.amount),
                )
            )

        revenue_amount = Decimal(revenue.amount)

        total_cost = sum(
            (
                contribution.expense_amount
                for contribution in contributions
            ),
            Decimal("0.00"),
        )

        profit = revenue_amount - total_cost

        return EventProfitabilityResult(
            event_id=event.id,
            event_reference=event_reference,
            revenue_reference=revenue.revenue_reference,
            revenue_amount=revenue_amount,
            currency=revenue.currency,
            cost_contributions=tuple(contributions),
            total_cost=total_cost,
            profit=profit,
        )


__all__ = [
    "CATERING_EVENT_CONTEXT_TYPE",
    "EventProfitabilityCostContribution",
    "EventProfitabilityResult",
    "EventProfitabilityService",
]
