"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.expense.models import Expense
from app.modules.expense.repositories import (
    ExpenseRepository,
)


class ExpenseService(
    CRUDService[Expense],
):
    """
    Application service for Expense entities.

    Provides the standard enterprise CRUD service boundary
    and pagination support.
    """

    def __init__(
        self,
        repository: ExpenseRepository | None = None,
    ) -> None:
        """
        Initialize the Expense service.

        Args:
            repository:
                Optional Expense repository. A default repository
                is created when one is not supplied.
        """

        super().__init__(
            repository
            or ExpenseRepository(),
            entity_name="Expense",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[Expense]:
        """
        Return a paginated Expense result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated Expense result.
        """

        return self.repository.paginate(
            options
        )


__all__ = [
    "ExpenseService",
]
