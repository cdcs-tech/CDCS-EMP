"""
Reporting read service for the Catering Event Profitability Register.

The service presents Catering-owned operational and financial evidence.
It does not persist reporting results or alter financial records.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import false, func, select
from sqlalchemy.exc import MultipleResultsFound

from app.extensions import db
from app.modules.catering.models import CateringEvent, Customer
from app.modules.catering.repositories.catering_revenue import (
    CateringRevenueRepository,
)
from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)
from app.modules.catering.repositories.expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.services.event_profitability import (
    CATERING_EVENT_CONTEXT_TYPE,
    EventProfitabilityService,
)
from app.modules.expense.models import Expense
from app.modules.expense.repositories.expense import ExpenseRepository


READINESS_REPORTABLE = "REPORTABLE"
READINESS_AWAITING_DATA = "AWAITING DATA"
READINESS_DATA_CONFLICT = "DATA CONFLICT"


@dataclass(frozen=True)
class CateringEventProfitabilityRegisterRow:
    event_id: int
    event_reference: str
    event_date: date
    customer_name: str
    operational_status: str
    financial_readiness: str
    recognized_revenue: Decimal | None = None
    consumed_costs: Decimal | None = None
    profit_or_loss: Decimal | None = None
    currency: str | None = None


@dataclass(frozen=True)
class CateringEventProfitabilityRegisterResult:
    items: tuple[CateringEventProfitabilityRegisterRow, ...]
    total_records: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.total_records == 0:
            return 0
        return (self.total_records + self.page_size - 1) // self.page_size

    @property
    def has_previous(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages


class CateringEventProfitabilityRegisterService:
    """Build a filtered, paginated, read-only profitability register."""

    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 100

    def __init__(
        self,
        *,
        revenue_repository: CateringRevenueRepository | None = None,
        association_repository: (
            CateringExpenseCostAssociationRepository | None
        ) = None,
        expense_repository: ExpenseRepository | None = None,
        profitability_service: EventProfitabilityService | None = None,
    ) -> None:
        self._revenue_repository = (
            revenue_repository or CateringRevenueRepository()
        )
        self._association_repository = (
            association_repository
            or CateringExpenseCostAssociationRepository()
        )
        self._expense_repository = (
            expense_repository or ExpenseRepository()
        )
        self._profitability_service = profitability_service

        if self._profitability_service is None:
            self._profitability_service = EventProfitabilityService(
                catering_event_repository=CateringEventRepository(),
                catering_revenue_repository=self._revenue_repository,
                expense_cost_association_repository=self._association_repository,
                expense_repository=self._expense_repository,
            )

    def get_register(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        operational_status: str | None = None,
        customer_id: int | None = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> CateringEventProfitabilityRegisterResult:
        if page < 1:
            raise ValueError("Page must be at least 1.")

        if page_size < 1 or page_size > self.MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size must be between 1 and {self.MAX_PAGE_SIZE}."
            )

        if date_from and date_to and date_from > date_to:
            raise ValueError("Start date cannot be after end date.")

        statement = (
            select(CateringEvent, Customer.name)
            .outerjoin(
                Customer,
                (Customer.id == CateringEvent.customer_id)
                & (Customer.is_deleted == false()),
            )
            .where(CateringEvent.is_deleted == false())
        )

        if date_from:
            statement = statement.where(
                CateringEvent.event_date >= date_from
            )

        if date_to:
            statement = statement.where(
                CateringEvent.event_date <= date_to
            )

        if operational_status:
            statement = statement.where(
                CateringEvent.status == operational_status
            )

        if customer_id is not None:
            statement = statement.where(
                CateringEvent.customer_id == customer_id
            )

        count_statement = (
            select(func.count())
            .select_from(statement.order_by(None).subquery())
        )
        total_records = int(
            db.session.execute(count_statement).scalar_one()
        )

        statement = (
            statement
            .order_by(
                CateringEvent.event_date.desc(),
                CateringEvent.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        records = db.session.execute(statement).all()

        rows = tuple(
            self._build_row(event, customer_name)
            for event, customer_name in records
        )

        return CateringEventProfitabilityRegisterResult(
            items=rows,
            total_records=total_records,
            page=page,
            page_size=page_size,
        )

    def _build_row(
        self,
        event: CateringEvent,
        customer_name: str | None,
    ) -> CateringEventProfitabilityRegisterRow:
        base = {
            "event_id": event.id,
            "event_reference": f"EVENT-{event.id}",
            "event_date": event.event_date,
            "customer_name": customer_name or "Customer unavailable",
            "operational_status": event.status,
        }

        try:
            revenue = (
                self._revenue_repository
                .get_recognized_by_event_id(event.id)
            )
        except MultipleResultsFound:
            return CateringEventProfitabilityRegisterRow(
                **base,
                financial_readiness=READINESS_DATA_CONFLICT,
            )

        if revenue is None:
            return CateringEventProfitabilityRegisterRow(
                **base,
                financial_readiness=READINESS_AWAITING_DATA,
            )

        associations = (
            self._association_repository
            .get_consumed_by_catering_context(
                CATERING_EVENT_CONTEXT_TYPE,
                f"EVENT-{event.id}",
            )
        )

        associations = [
            association
            for association in associations
            if not association.is_deleted
        ]

        if not associations:
            return CateringEventProfitabilityRegisterRow(
                **base,
                financial_readiness=READINESS_AWAITING_DATA,
            )

        expenses: list[Expense] = []

        for association in associations:
            expense = self._expense_repository.get_by_id(
                association.expense_id
            )

            if expense is None or expense.is_deleted:
                return CateringEventProfitabilityRegisterRow(
                    **base,
                    financial_readiness=READINESS_DATA_CONFLICT,
                )

            expenses.append(expense)

        expense_currencies = [
            getattr(expense, "currency", None)
            for expense in expenses
        ]

        if any(not currency for currency in expense_currencies):
            return CateringEventProfitabilityRegisterRow(
                **base,
                financial_readiness=READINESS_AWAITING_DATA,
            )

        if any(
            currency != revenue.currency
            for currency in expense_currencies
        ):
            return CateringEventProfitabilityRegisterRow(
                **base,
                financial_readiness=READINESS_DATA_CONFLICT,
            )

        # Profitability is reportable only when every consumed expense
        # has verified currency evidence matching the recognized revenue.
        result = self._profitability_service.calculate_for_event(
            event.id
        )

        return CateringEventProfitabilityRegisterRow(
            **base,
            financial_readiness=READINESS_REPORTABLE,
            recognized_revenue=result.revenue_amount,
            consumed_costs=result.total_cost,
            profit_or_loss=result.profit,
            currency=result.currency,
        )


__all__ = [
    "CateringEventProfitabilityRegisterRow",
    "CateringEventProfitabilityRegisterResult",
    "CateringEventProfitabilityRegisterService",
    "READINESS_REPORTABLE",
    "READINESS_AWAITING_DATA",
    "READINESS_DATA_CONFLICT",
]
