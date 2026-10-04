"""
C6.7 end-to-end integration test.

Verifies the real Catering Event profitability composition path
from recognized Catering Revenue and consumed Catering Expense
contributions backed by authoritative Expense records.
"""

from datetime import date
from decimal import Decimal

from app.extensions import db
from app.modules.catering.models import (
    CateringEvent,
    CateringExpenseCostAssociation,
    CateringRequest,
    CateringRevenue,
    Customer,
)
from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)
from app.modules.catering.repositories.catering_revenue import (
    CateringRevenueRepository,
)
from app.modules.catering.repositories.expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.services.event_profitability import (
    EventProfitabilityService,
)
from app.modules.catering.workflows import CateringRevenueWorkflow
from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)
from app.modules.expense.repositories.expense import ExpenseRepository
from app.modules.expense.workflows.expense import APPROVED


def test_event_profitability_composes_authoritative_revenue_and_consumed_costs(
    app,
):
    """
    Compose profitability from real persisted Catering and Expense data.

    Recognized Catering Revenue is the authoritative revenue amount.

    Consumed Catering Expense Cost Associations identify the costs
    attributable to the Event, while Expense.amount remains the
    authoritative cost amount.

    An eligible-but-unconsumed cost contribution must not be included.
    """

    with app.app_context():
        customer = Customer(
            name="C6.7 Profitability Customer",
            customer_type="ORGANIZATION",
        )
        db.session.add(customer)
        db.session.flush()

        request = CateringRequest(
            customer_id=customer.id,
            request_date=date(2026, 9, 29),
            requested_service="Catering Profitability Test",
            service_date=date(2026, 10, 1),
            attendance=50,
        )
        db.session.add(request)
        db.session.flush()

        event = CateringEvent(
            request_id=request.id,
            customer_id=customer.id,
            event_date=date(2026, 10, 1),
            service_details="C6.7 profitability validation event",
            attendance=50,
            status="COMPLETED",
        )
        db.session.add(event)
        db.session.flush()

        revenue = CateringRevenue(
            revenue_reference="CAT-REV-C6.7-E2E-001",
            source_type="CATERING_EVENT",
            source_reference=f"EVENT-{event.id}",
            customer_id=customer.id,
            event_id=event.id,
            amount=Decimal("1250.00"),
            currency="USD",
            revenue_date=date(2026, 10, 1),
            revenue_classification="CATERING_SERVICE",
            status=CateringRevenueWorkflow.RECOGNIZED,
        )
        db.session.add(revenue)
        db.session.flush()

        classification = ExpenseClassification(
            code="C6.7-CATERING-OPERATIONS",
            name="C6.7 Catering Operations",
            description="C6.7 profitability test expense classification.",
        )
        db.session.add(classification)
        db.session.flush()

        consumed_expense = Expense(
            classification_id=classification.id,
            description="C6.7 consumed catering cost",
            amount=Decimal("150.00"),
            expense_date=date(2026, 9, 29),
            status=APPROVED,
        )
        db.session.add(consumed_expense)
        db.session.flush()

        eligible_expense = Expense(
            classification_id=classification.id,
            description="C6.7 eligible but unconsumed catering cost",
            amount=Decimal("75.00"),
            expense_date=date(2026, 9, 30),
            status=APPROVED,
        )
        db.session.add(eligible_expense)
        db.session.flush()

        event_reference = f"EVENT-{event.id}"

        consumed_association = CateringExpenseCostAssociation(
            expense_id=consumed_expense.id,
            catering_context_type="CATERING_EVENT",
            catering_context_reference=event_reference,
            status="CONSUMED",
            contribution_id="C6.7-COST-CONSUMED-001",
        )
        db.session.add(consumed_association)
        db.session.flush()

        eligible_association = CateringExpenseCostAssociation(
            expense_id=eligible_expense.id,
            catering_context_type="CATERING_EVENT",
            catering_context_reference=event_reference,
            status="ELIGIBLE",
            contribution_id="C6.7-COST-ELIGIBLE-001",
        )
        db.session.add(eligible_association)
        db.session.flush()

        event_id = event.id
        revenue_id = revenue.id
        consumed_expense_id = consumed_expense.id
        eligible_expense_id = eligible_expense.id

        db.session.commit()

        service = EventProfitabilityService(
            catering_event_repository=CateringEventRepository(),
            catering_revenue_repository=CateringRevenueRepository(),
            expense_cost_association_repository=(
                CateringExpenseCostAssociationRepository()
            ),
            expense_repository=ExpenseRepository(),
        )

        result = service.calculate_for_event(event_id)

        assert result.event_id == event_id
        assert result.event_reference == event_reference
        assert result.revenue_reference == "CAT-REV-C6.7-E2E-001"
        assert result.revenue_amount == Decimal("1250.00")
        assert result.currency == "USD"

        assert result.total_cost == Decimal("150.00")
        assert result.profit == Decimal("1100.00")

        assert len(result.cost_contributions) == 1

        contribution = result.cost_contributions[0]

        assert contribution.association_id == consumed_association.id
        assert (
            contribution.contribution_id
            == "C6.7-COST-CONSUMED-001"
        )
        assert contribution.expense_id == consumed_expense_id
        assert contribution.expense_amount == Decimal("150.00")

        assert contribution.expense_id != eligible_expense_id

        persisted_event = db.session.get(
            CateringEvent,
            event_id,
        )
        persisted_revenue = db.session.get(
            CateringRevenue,
            revenue_id,
        )
        persisted_consumed_expense = db.session.get(
            Expense,
            consumed_expense_id,
        )

        assert persisted_event is not None
        assert persisted_revenue is not None
        assert persisted_consumed_expense is not None

        assert (
            persisted_revenue.status
            == CateringRevenueWorkflow.RECOGNIZED
        )
        assert persisted_consumed_expense.amount == Decimal("150.00")
