"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock movement service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.crud import (
    CRUDService,
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockMovement
from app.modules.catering.repositories import StockMovementRepository

class StockMovementService(
    CRUDService[StockMovement],
):
    """
    Application service for Catering StockMovement entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and movement-specific retrieval
    operations.

    Movement posting, balance updates, immutability rules,
    and inventory transaction orchestration are intentionally
    deferred to subsequent Inventory service stages.
    """

    def __init__(
        self,
        repository: StockMovementRepository | None = None,
        transaction_manager: TransactionManager | None = None,
    ) -> None:
        """
        Initialize the StockMovement service.

        Args:
            repository:
                Optional StockMovement repository. A default
                repository is created when one is not supplied.

            transaction_manager:
                Optional transaction manager. A default SQLAlchemy
                transaction manager is created when one is not supplied.
        """

        super().__init__(
            repository
            or StockMovementRepository(),
            entity_name="StockMovement",
        )

        self.transaction_manager = (
            transaction_manager
            or SQLAlchemyTransactionManager()
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[StockMovement]:
        """
        Return a paginated StockMovement result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated StockMovement result.
        """

        return self.repository.paginate(
            options
        )

    def get_by_reference(
        self,
        reference: str,
    ) -> StockMovement | None:
        """
        Retrieve a StockMovement by its reference.

        Args:
            reference:
                Movement reference.

        Returns:
            The matching StockMovement, or None when no movement
            exists with the supplied reference.
        """

        return self.repository.get_by_reference(
            reference
        )


__all__ = [
    "StockMovementService",
]
