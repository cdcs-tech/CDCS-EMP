"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Supplier repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.procurement.models import (
    Supplier,
)


class SupplierRepository(
    SQLAlchemyRepository[Supplier],
):
    """
    Repository for Procurement Supplier entities.

    Provides the standard enterprise persistence, query,
    filtering, sorting, and pagination capabilities.
    """

    def __init__(self) -> None:
        """
        Initialize the Supplier repository.
        """

        super().__init__(
            Supplier
        )


__all__ = [
    "SupplierRepository",
]
