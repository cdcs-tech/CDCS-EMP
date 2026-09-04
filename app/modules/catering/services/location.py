"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory location service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import InventoryLocation
from app.modules.catering.repositories import (
    InventoryLocationRepository,
)


class InventoryLocationService(
    CRUDService[InventoryLocation],
):
    """
    Application service for Catering InventoryLocation entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and location-specific retrieval
    operations.
    """

    def __init__(
        self,
        repository: InventoryLocationRepository | None = None,
    ) -> None:
        """
        Initialize the InventoryLocation service.

        Args:
            repository:
                Optional InventoryLocation repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or InventoryLocationRepository(),
            entity_name="InventoryLocation",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[InventoryLocation]:
        """
        Return a paginated InventoryLocation result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated InventoryLocation result.
        """

        return self.repository.paginate(
            options
        )

    def get_by_code(
        self,
        code: str,
    ) -> InventoryLocation | None:
        """
        Retrieve an InventoryLocation by its unique code.

        Args:
            code:
                Unique inventory location code.

        Returns:
            The matching InventoryLocation, or None when
            no location exists with the supplied code.
        """

        return self.repository.get_by_code(
            code
        )


__all__ = [
    "InventoryLocationService",
]
