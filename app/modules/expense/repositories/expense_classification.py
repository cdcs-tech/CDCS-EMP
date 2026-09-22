"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense classification repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.expense.models import (
    ExpenseClassification,
)


class ExpenseClassificationRepository(
    SQLAlchemyRepository[ExpenseClassification],
):
    """
    Repository for ExpenseClassification entities.
    """

    def __init__(self) -> None:
        """
        Initialize the ExpenseClassification repository.
        """

        super().__init__(
            ExpenseClassification
        )


__all__ = [
    "ExpenseClassificationRepository",
]
