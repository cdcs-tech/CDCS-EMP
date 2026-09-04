"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock item service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockItem
from app.modules.catering.repositories import StockItemRepository


class StockItemService(
    CRUDService[StockItem],
):
    """
    Application service for Catering StockItem entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and StockItem-specific retrieval
    operations.
    """

    def __init__(
        self,
        repository: StockItemRepository | None = None,
    ) -> None:
        """
        Initialize the StockItem service.

        Args:
            repository:
                Optional StockItem repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or StockItemRepository(),
            entity_name="StockItem",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[StockItem]:
        """
        Return a paginated StockItem result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated StockItem result.
        """

        return self.repository.paginate(
            options
        )

    def get_by_product_id(
        self,
        product_id: int,
    ) -> StockItem | None:
        """
        Retrieve the StockItem associated with a Product.

        Args:
            product_id:
                Identifier of the Product.

        Returns:
            The associated StockItem, or None when no
            StockItem exists for the Product.
        """

        return self.repository.get_by_product_id(
            product_id
        )

    def exists_for_product(
        self,
        product_id: int,
    ) -> bool:
        """
        Determine whether a StockItem exists for a Product.

        Args:
            product_id:
                Identifier of the Product.

        Returns:
            True when a StockItem exists for the Product.
        """

        return self.repository.exists_for_product(
            product_id
        )


__all__ = [
    "StockItemService",
]
