"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase requirement repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.procurement.models import (
    PurchaseRequirement,
)


class PurchaseRequirementRepository(
    SQLAlchemyRepository[PurchaseRequirement],
):
    """
    Repository for Procurement PurchaseRequirement entities.

    Provides the standard enterprise persistence, query,
    filtering, sorting, and pagination capabilities.
    """

    def __init__(self) -> None:
        """
        Initialize the PurchaseRequirement repository.
        """

        super().__init__(
            PurchaseRequirement
        )


__all__ = [
    "PurchaseRequirementRepository",
]
