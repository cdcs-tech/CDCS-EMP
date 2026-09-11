"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Supplier service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.procurement.models import Supplier
from app.modules.procurement.repositories import SupplierRepository


class SupplierService(
    CRUDService[Supplier],
):
    """
    Application service for Procurement Supplier entities.

    Provides the standard enterprise CRUD service boundary
    and pagination support.

    Supplier lifecycle transitions remain outside this
    service until the dedicated Procurement Workflow stage.
    """

    def __init__(
        self,
        repository: SupplierRepository | None = None,
    ) -> None:
        """
        Initialize the Supplier service.

        Args:
            repository:
                Optional Supplier repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or SupplierRepository(),
            entity_name="Supplier",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[Supplier]:
        """
        Return a paginated Supplier result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated Supplier result.
        """

        return self.repository.paginate(
            options
        )


__all__ = [
    "SupplierService",
]
