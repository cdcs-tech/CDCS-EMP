"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock transfer service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockTransfer
from app.modules.catering.repositories import StockTransferRepository


class StockTransferService(
    CRUDService[StockTransfer],
):
    """
    Application service for Catering StockTransfer entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and transfer-specific retrieval
    operations.

    Transfer validation, posting, balance updates, and
    orchestration are intentionally deferred to subsequent
    Inventory service stages.
    """

    def __init__(
        self,
        repository: StockTransferRepository | None = None,
    ) -> None:
        """
        Initialize the StockTransfer service.

        Args:
            repository:
                Optional StockTransfer repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or StockTransferRepository(),
            entity_name="StockTransfer",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[StockTransfer]:
        """
        Return a paginated StockTransfer result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated StockTransfer result.
        """

        return self.repository.paginate(
            options
        )

    def get_by_reference(
        self,
        reference: str,
    ) -> StockTransfer | None:
        """
        Retrieve a StockTransfer by its unique reference.

        Args:
            reference:
                Unique transfer reference.

        Returns:
            The matching StockTransfer, or None when no transfer
            exists with the supplied reference.
        """

        return self.repository.get_by_reference(
            reference
        )


__all__ = [
    "StockTransferService",
]
