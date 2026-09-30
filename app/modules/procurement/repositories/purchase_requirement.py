"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase requirement repository.
"""

from sqlalchemy import (
    select,
)

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import (
    db,
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

    def get_by_reference(
        self,
        reference: str,
    ) -> PurchaseRequirement | None:
        """
        Return a PurchaseRequirement by its unique reference.

        Procurement-specific reference lookup belongs in the
        Procurement repository so callers do not contain
        SQLAlchemy query logic.
        """

        statement = select(
            PurchaseRequirement,
        ).where(
            PurchaseRequirement.reference == reference,
        )

        return db.session.execute(
            statement,
        ).scalar_one_or_none()


__all__ = [
    "PurchaseRequirementRepository",
]
