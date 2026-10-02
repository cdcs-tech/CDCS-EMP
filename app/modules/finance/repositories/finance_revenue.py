"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Finance Revenue repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.finance.models import (
    FinanceRevenue,
)


class FinanceRevenueRepository(
    SQLAlchemyRepository[FinanceRevenue],
):
    """
    Repository for Finance Revenue entities.
    """

    def __init__(self) -> None:
        """
        Initialize the Finance Revenue repository.
        """

        super().__init__(
            FinanceRevenue
        )


__all__ = [
    "FinanceRevenueRepository",
]
