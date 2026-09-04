"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock balance service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockBalance
from app.modules.catering.repositories import StockBalanceRepository


class StockBalanceService(
    CRUDService[StockBalance],
):
    """
    Application service for Catering StockBalance entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and balance retrieval operations.

    Inventory balance business rules are intentionally deferred
    to the inventory transaction/orchestration stages.
    """

    def __init__(
        self,
        repository: StockBalanceRepository | None = None,
    ) -> None:
        """
        Initialize the StockBalance service.

        Args:
            repository:
                Optional StockBalance repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or StockBalanceRepository(),
            entity_name="StockBalance",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[StockBalance]:
        """
        Return a paginated StockBalance result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated StockBalance result.
        """

        return self.repository.paginate(
            options
        )

    def get_by_stock_item_and_location(
        self,
        stock_item_id: int,
        location_id: int,
    ) -> StockBalance | None:
        """
        Retrieve the balance for a StockItem at a Location.

        Args:
            stock_item_id:
                Identifier of the StockItem.

            location_id:
                Identifier of the InventoryLocation.

        Returns:
            The matching StockBalance, or None when no balance
            exists for the supplied StockItem and Location.
        """

        return self.repository.get_by_stock_item_and_location(
            stock_item_id,
            location_id,
        )

    def get_by_stock_item(
        self,
        stock_item_id: int,
    ) -> list[StockBalance]:
        """
        Retrieve all location balances for a StockItem.

        Args:
            stock_item_id:
                Identifier of the StockItem.

        Returns:
            All StockBalance records associated with the StockItem.
        """

        return self.repository.get_by_stock_item(
            stock_item_id
        )

    def get_by_location(
        self,
        location_id: int,
    ) -> list[StockBalance]:
        """
        Retrieve all StockItem balances at a Location.

        Args:
            location_id:
                Identifier of the InventoryLocation.

        Returns:
            All StockBalance records associated with the Location.
        """

        return self.repository.get_by_location(
            location_id
        )


__all__ = [
    "StockBalanceService",
]
