"""
C5 end-to-end integration test.

Verifies the real Catering Revenue recognition execution path through
the enterprise post-commit integration boundary into Finance.
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
    CateringRequest,
    CateringRevenue,
    Customer,
)
from app.modules.catering.workflows import (
    CateringRevenueWorkflow,
)
from app.modules.finance.models import FinanceRevenue


def test_recognized_catering_revenue_is_delivered_to_finance_after_commit(
    app,
    admin_user,
):
    """
    A recognized Catering Revenue is delivered through the real
    enterprise post-commit boundary and represented once in Finance.
    """

    with app.app_context():
        administrator_role = (
            db.session.query(Role)
            .filter_by(name="Administrator")
            .one()
        )

        permission = Permission(
            name="catering.catering_revenue.recognize",
            module="CATERING",
            description="Recognize Catering Revenue.",
        )
        db.session.add(permission)
        db.session.flush()

        db.session.add(
            RolePermission(
                role=administrator_role,
                permission=permission,
            )
        )
        db.session.flush()

        customer = Customer(
            name="C5 E2E Customer",
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

        revenue = CateringRevenue(
            revenue_reference="CAT-REV-C5-E2E-001",
            source_type="CATERING_EVENT",
            source_reference=f"EVENT-{event.id}",
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
        db.session.commit()

        dispatcher = app.extensions["command_dispatcher"]

        context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="CATERING",
            operation="catering.revenue.recognize",
        )

        result = dispatcher.dispatch(
            RecognizeCateringRevenueCommand(
                revenue_id=revenue_id,
            ),
            context,
        )

        assert result.is_success()

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

        assert recognized_revenue is not None
        assert (
            recognized_revenue.status
            == CateringRevenueWorkflow.RECOGNIZED
        )
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
        assert finance_revenue.source_reference == f"EVENT-{event.id}"
        assert finance_revenue.amount == Decimal("1250.00")
        assert finance_revenue.currency == "USD"
        assert finance_revenue.revenue_date == date(2026, 10, 1)
        assert (
            finance_revenue.revenue_classification
            == "CATERING_SERVICE"
        )
        assert finance_revenue.status == "PENDING"
