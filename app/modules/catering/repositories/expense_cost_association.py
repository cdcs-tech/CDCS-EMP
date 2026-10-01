"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Expense Cost Association repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.catering.models import CateringExpenseCostAssociation


class CateringExpenseCostAssociationRepository(
    SQLAlchemyRepository[CateringExpenseCostAssociation],
):
    """
    Repository for Catering Expense Cost Association entities.

    Provides persistence access without owning Expense lifecycle,
    integration delivery, or Catering costing rules.
    """

    def __init__(self) -> None:
        """
        Initialize the Catering Expense Cost Association repository.
        """

        super().__init__(
            CateringExpenseCostAssociation,
        )


__all__ = [
    "CateringExpenseCostAssociationRepository",
]
