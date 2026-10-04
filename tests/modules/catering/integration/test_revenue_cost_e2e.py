"""
C6.6 end-to-end composition test.

Verifies that the completed Catering Revenue → Finance and
Approved Expense → Catering Cost integrations can coexist for
the same Catering Event without violating ownership boundaries.
"""

from datetime import date
from decimal import Decimal

from app.core.execution import ExecutionContext
from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.modules.catering.commands import (
    RecognizeCateringRevenueCommand,
)
from app.modules.catering.models import (
    CateringEvent,
    CateringExpenseCostAssociation,
    CateringRequest,
    CateringRevenue,
    Customer,
)
from app.modules.catering.workflows import (
    CateringRevenueWorkflow,
)
from app.modules.expense.commands import (
    ApproveExpenseCommand,
)
from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)
from app.modules.finance.models import FinanceRevenue


def test_revenue_and_approved_cost_coexist_for_same_catering_event(
    app,
    admin_user,
):
    """
    A Catering Event can independently produce a recognized
    revenue fact delivered to Finance and an approved Expense
    consumed as a Catering cost contribution.
    """

    with app.app_context():
        administrator_role = (
            db.session.query(Role)
            .filter_by(name="Administrator")
            .one()
        )

        revenue_permission = Permission(
            name="catering.catering_revenue.recognize",
            module="CATERING",
            description="Recognize Catering Revenue.",
        )

        expense_permission = Permission(
            name="expense.expense.approve",
            module="EXPENSE",
            description="Approve expenses.",
        )

        db.session.add_all(
            [
                revenue_permission,
                expense_permission,
            ]
        )
        db.session.flush()

        db.session.add_all(
            [
                RolePermission(
                    role=administrator_role,
                    permission=revenue_permission,
                ),
                RolePermission(
                    role=administrator_role,
                    permission=expense_permission,
                ),
            ]
        )
        db.session.flush()

        customer = Customer(
            name="C6.6 E2E Customer",
            customer_type="ORGANIZATION",
        )
        db.session.add(customer)
        db.session.flush()

        request = CateringRequest(
            customer_id=customer.id,
            request_date=date(2026, 9, 29),
            requested_service="Corporate Catering",
            service_date=date(2026, 10, 1),
            attendance=50,
        )
        db.session.add(request)
        db.session.flush()

        event = CateringEvent(
            request_id=request.id,
            customer_id=customer.id,
            event_date=date(2026, 10, 1),
            service_details="Corporate catering service",
            attendance=50,
            status="COMPLETED",
        )
        db.session.add(event)
        db.session.flush()

        event_reference = f"EVENT-{event.id}"

        revenue = CateringRevenue(
            revenue_reference="CAT-REV-C6.6-E2E-001",
            source_type="CATERING_EVENT",
            source_reference=event_reference,
            customer_id=customer.id,
            event_id=event.id,
            amount=Decimal("1250.00"),
            currency="USD",
            revenue_date=date(2026, 10, 1),
            revenue_classification="CATERING_SERVICE",
            status=CateringRevenueWorkflow.DRAFT,
        )
        db.session.add(revenue)
        db.session.flush()

        revenue_id = revenue.id
        revenue_reference = revenue.revenue_reference

        revenue.status = CateringRevenueWorkflow.ELIGIBLE

        classification = ExpenseClassification(
            code="CATERING-OPERATIONS",
            name="Catering Operations",
            description="Catering operational expenses.",
        )
        db.session.add(classification)
        db.session.flush()

        expense = Expense(
            classification_id=classification.id,
            description="Catering food supplies",
            amount=Decimal("150.00"),
            expense_date=date(2026, 9, 29),
            status="SUBMITTED",
        )
        db.session.add(expense)
        db.session.flush()

        association = CateringExpenseCostAssociation(
            expense_id=expense.id,
            catering_context_type="EVENT",
            catering_context_reference=event_reference,
            status="ELIGIBLE",
            contribution_id=(
                f"expense:{expense.id}:"
                "catering:consume_approved_expense"
            ),
        )
        db.session.add(association)
        db.session.flush()

        expense_id = expense.id
        association_id = association.id

        db.session.commit()

        dispatcher = app.extensions["command_dispatcher"]

        revenue_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="CATERING",
            operation="catering.revenue.recognize",
        )

        revenue_result = dispatcher.dispatch(
            RecognizeCateringRevenueCommand(
                revenue_id=revenue_id,
            ),
            revenue_context,
        )

        assert revenue_result.is_success()

        expense_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="EXPENSE",
            operation="expense.approve",
        )

        expense_result = dispatcher.dispatch(
            ApproveExpenseCommand(
                expense_id=expense_id,
            ),
            expense_context,
        )

        assert expense_result.is_success()

        db.session.expire_all()

        recognized_revenue = db.session.get(
            CateringRevenue,
            revenue_id,
        )

        finance_revenues = (
            db.session.query(FinanceRevenue)
            .filter_by(
                contribution_reference=revenue_reference,
            )
            .all()
        )

        approved_expense = db.session.get(
            Expense,
            expense_id,
        )

        consumed_association = db.session.get(
            CateringExpenseCostAssociation,
            association_id,
        )

        assert recognized_revenue is not None
        assert (
            recognized_revenue.status
            == CateringRevenueWorkflow.RECOGNIZED
        )
        assert recognized_revenue.event_id == event.id
        assert recognized_revenue.source_reference == event_reference
        assert recognized_revenue.recognized_at is not None

        assert len(finance_revenues) == 1

        finance_revenue = finance_revenues[0]

        assert (
            finance_revenue.contribution_reference
            == revenue_reference
        )
        assert (
            finance_revenue.revenue_reference
            == revenue_reference
        )
        assert finance_revenue.source_type == "CATERING_EVENT"
        assert finance_revenue.source_reference == event_reference
        assert finance_revenue.amount == Decimal("1250.00")
        assert finance_revenue.currency == "USD"
        assert finance_revenue.revenue_date == date(2026, 10, 1)
        assert (
            finance_revenue.revenue_classification
            == "CATERING_SERVICE"
        )
        assert finance_revenue.status == "PENDING"

        assert approved_expense is not None
        assert approved_expense.status == "APPROVED"
        assert approved_expense.approved_at is not None

        assert consumed_association is not None
        assert consumed_association.status == "CONSUMED"
        assert consumed_association.consumed_at is not None
        assert (
            consumed_association.expense_id
            == approved_expense.id
        )
        assert (
            consumed_association.catering_context_type
            == "EVENT"
        )
        assert (
            consumed_association.catering_context_reference
            == event_reference
        )
        assert (
            consumed_association.contribution_id
            == association.contribution_id
        )
