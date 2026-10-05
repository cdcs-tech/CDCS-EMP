"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Customer repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.catering.models import (
    Customer,
)


class CustomerRepository(
    SQLAlchemyRepository[Customer],
):
    """
    Repository for Catering Customer entities.
    """

    def __init__(self) -> None:
        """
        Initialize the Customer repository.
        """

        super().__init__(
            Customer
        )


__all__ = [
    "CustomerRepository",
]
