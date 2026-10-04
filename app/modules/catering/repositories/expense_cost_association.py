"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Expense Cost Association repository.
"""

from __future__ import annotations

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import (
    CateringExpenseCostAssociation,
)


class CateringExpenseCostAssociationRepository(
    SQLAlchemyRepository[CateringExpenseCostAssociation],
):
    """
    Repository for Catering Expense Cost Associations.

    Provides persistence access for Catering-owned Expense
    Cost Associations without owning Expense lifecycle,
    integration delivery, or costing rules.
    """

    def __init__(self) -> None:
        """
        Initialize the Catering Expense Cost Association repository.
        """

        super().__init__(
            CateringExpenseCostAssociation
        )

    def get_eligible_by_expense_id(
        self,
        expense_id: int,
    ) -> list[CateringExpenseCostAssociation]:
        """
        Return all eligible Catering associations for an Expense.

        The lookup is intentionally scoped to Catering-owned
        association state. It does not access or interpret the
        Expense entity or its lifecycle.
        """

        statement = (
            select(
                CateringExpenseCostAssociation
            )
            .where(
                CateringExpenseCostAssociation.expense_id
                == expense_id
            )
            .where(
                CateringExpenseCostAssociation.status
                == "ELIGIBLE"
            )
        )

        return list(
            db.session.execute(
                statement
            )
            .scalars()
            .all()
        )

    def get_by_contribution_id(
        self,
        contribution_id: str,
    ) -> CateringExpenseCostAssociation | None:
        """
        Return the Catering Expense Cost Association
        for a stable contribution ID.
        """

        statement = (
            select(
                CateringExpenseCostAssociation
            )
            .where(
                CateringExpenseCostAssociation.contribution_id
                == contribution_id
            )
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def get_consumed_by_catering_context(
        self,
        catering_context_type: str,
        catering_context_reference: str,
    ) -> list[CateringExpenseCostAssociation]:
        """
        Return consumed Catering associations for a Catering context.

        The lookup is intentionally scoped to Catering-owned
        association state. It does not access or interpret the
        associated Expense entity or its lifecycle.
        """

        statement = (
            select(
                CateringExpenseCostAssociation
            )
            .where(
                CateringExpenseCostAssociation.catering_context_type
                == catering_context_type
            )
            .where(
                CateringExpenseCostAssociation.catering_context_reference
                == catering_context_reference
            )
            .where(
                CateringExpenseCostAssociation.status
                == "CONSUMED"
            )
        )

        return list(
            db.session.execute(
                statement
            )
            .scalars()
            .all()
        )


__all__ = [
    "CateringExpenseCostAssociationRepository",
]
