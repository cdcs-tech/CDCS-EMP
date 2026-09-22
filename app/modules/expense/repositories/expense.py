"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.expense.models import (
    Expense,
)


class ExpenseRepository(
    SQLAlchemyRepository[Expense],
):
    """
    Repository for Expense entities.
    """

    def __init__(self) -> None:
        """
        Initialize the Expense repository.
        """

        super().__init__(
            Expense
        )


__all__ = [
    "ExpenseRepository",
]
