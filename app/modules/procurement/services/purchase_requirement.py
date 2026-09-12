"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase requirement service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.procurement.models import PurchaseRequirement
from app.modules.procurement.repositories import (
    PurchaseRequirementRepository,
)


class PurchaseRequirementService(
    CRUDService[PurchaseRequirement],
):
    """
    Application service for Procurement PurchaseRequirement
    entities.

    Provides the standard enterprise CRUD service boundary
    and pagination support.

    PurchaseRequirement lifecycle transitions remain outside
    this service until the dedicated Procurement Workflow
    stage.
    """

    def __init__(
        self,
        repository: PurchaseRequirementRepository | None = None,
    ) -> None:
        """
        Initialize the PurchaseRequirement service.

        Args:
            repository:
                Optional PurchaseRequirement repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or PurchaseRequirementRepository(),
            entity_name="PurchaseRequirement",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[PurchaseRequirement]:
        """
        Return a paginated PurchaseRequirement result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated PurchaseRequirement result.
        """

        return self.repository.paginate(
            options
        )


__all__ = [
    "PurchaseRequirementService",
]
