"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense classification service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.expense.models import ExpenseClassification
from app.modules.expense.repositories import (
    ExpenseClassificationRepository,
)


class ExpenseClassificationService(
    CRUDService[ExpenseClassification],
):
    """
    Application service for ExpenseClassification entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and classification lifecycle operations.
    """

    def __init__(
        self,
        repository: ExpenseClassificationRepository | None = None,
    ) -> None:
        """
        Initialize the ExpenseClassification service.

        Args:
            repository:
                Optional ExpenseClassification repository.
                A default repository is created when one is not
                supplied.
        """

        super().__init__(
            repository
            or ExpenseClassificationRepository(),
            entity_name="ExpenseClassification",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[ExpenseClassification]:
        """
        Return a paginated ExpenseClassification result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated ExpenseClassification result.
        """

        return self.repository.paginate(
            options
        )

    def activate(
        self,
        entity_id,
    ) -> ExpenseClassification:
        """
        Activate an ExpenseClassification entity.

        Args:
            entity_id:
                Identifier of the ExpenseClassification to activate.

        Returns:
            The activated ExpenseClassification entity.
        """

        classification = self.get(
            entity_id
        )

        classification.is_active = True

        return self.update(
            classification
        )

    def deactivate(
        self,
        entity_id,
    ) -> ExpenseClassification:
        """
        Deactivate an ExpenseClassification entity.

        Args:
            entity_id:
                Identifier of the ExpenseClassification to deactivate.

        Returns:
            The deactivated ExpenseClassification entity.
        """

        classification = self.get(
            entity_id
        )

        classification.is_active = False

        return self.update(
            classification
        )


__all__ = [
    "ExpenseClassificationService",
]
