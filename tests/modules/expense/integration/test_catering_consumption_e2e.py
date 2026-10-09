"""
C4 end-to-end integration test.

Verifies the real Expense approval execution path through
the enterprise post-commit integration boundary into Catering.
"""

from datetime import date
from decimal import Decimal

from app.core.execution import ExecutionContext
from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.modules.catering.models import (
    CateringExpenseCostAssociation,
)
from app.modules.expense.commands import (
    ApproveExpenseCommand,
)
from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)


def test_approved_expense_is_consumed_by_catering_after_commit(
    app,
    admin_user,
):
    """
    An approved Expense with an explicit eligible Catering
    association is delivered through the real enterprise
    post-commit boundary and consumed by Catering.
    """

    with app.app_context():
        administrator_role = (
            db.session.query(Role)
            .filter_by(name="Administrator")
            .one()
        )

        approval_permission = Permission(
            name="expense.expense.approve",
            module="EXPENSE",
            description="Approve expenses.",
        )

        db.session.add(approval_permission)
        db.session.flush()

        db.session.add(
            RolePermission(
                role=administrator_role,
                permission=approval_permission,
            )
        )
        db.session.flush()

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
            catering_context_type="CATERING_EVENT",
            catering_context_reference="EVENT-1",
            status="ELIGIBLE",
            contribution_id=(
                f"expense:{expense.id}:"
                "catering:consume_approved_expense"
            ),
        )

        db.session.add(association)
        db.session.commit()

        dispatcher = app.extensions[
            "command_dispatcher"
        ]

        context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="EXPENSE",
            operation="expense.approve",
        )

        result = dispatcher.dispatch(
            ApproveExpenseCommand(
                expense_id=expense.id,
            ),
            context,
        )

        assert result.is_success()

        db.session.expire_all()

        approved_expense = db.session.get(
            Expense,
            expense.id,
        )

        consumed_association = db.session.get(
            CateringExpenseCostAssociation,
            association.id,
        )

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
            consumed_association.contribution_id
            == association.contribution_id
        )
