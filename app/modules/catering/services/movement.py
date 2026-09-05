"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock movement service.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.crud import (
    CRUDService,
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.data import PaginatedResult, QueryOptions
from app.modules.catering.models import StockMovement
from app.modules.catering.models.stock_balance import StockBalance
from app.modules.catering.repositories import StockMovementRepository
from app.modules.catering.repositories.balance import (
    StockBalanceRepository,
)


class StockMovementService(
    CRUDService[StockMovement],
):
    """
    Application service for Catering StockMovement entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, movement-specific retrieval operations,
    and inventory movement posting.

    Movement posting is performed atomically through the enterprise
    transaction boundary. Posted movements update the authoritative
    StockBalance and become immutable business transactions.
    """

    def __init__(
        self,
        repository: StockMovementRepository | None = None,
        transaction_manager: TransactionManager | None = None,
        balance_repository: StockBalanceRepository | None = None,
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

            balance_repository:
                Optional StockBalance repository. A default repository
                is created when one is not supplied.
        """

        super().__init__(
            repository or StockMovementRepository(),
            entity_name="StockMovement",
        )

        self.transaction_manager = (
            transaction_manager
            or SQLAlchemyTransactionManager()
        )

        self.balance_repository = (
            balance_repository
            or StockBalanceRepository()
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

    def post_movement(
        self,
        movement: StockMovement,
    ) -> StockMovement:
        """
        Post an inventory movement atomically.

        A posted movement updates the authoritative StockBalance
        and becomes immutable.

        Draft movements have no inventory effect.

        Raises:
            ValueError:
                If the movement is invalid, already posted, references
                incomplete inventory data, or would produce an invalid
                stock balance.
        """

        if movement is None:
            raise ValueError(
                "Movement is required."
            )

        if movement.status == "POSTED":
            raise ValueError(
                "Movement is already posted."
            )

        if movement.movement_type not in {
            "OPENING_BALANCE",
            "RECEIPT",
            "ISSUE",
            "ADJUSTMENT",
            "TRANSFER",
        }:
            raise ValueError(
                "Invalid movement type."
            )

        if movement.quantity == 0:
            raise ValueError(
                "Movement quantity cannot be zero."
            )

        if movement.stock_item_id is None:
            raise ValueError(
                "Stock item is required."
            )

        if movement.location_id is None:
            raise ValueError(
                "Inventory location is required."
            )

        with self.transaction_manager.transaction():

            balance = (
                self.balance_repository
                .get_by_stock_item_and_location(
                    movement.stock_item_id,
                    movement.location_id,
                )
            )

            if balance is None:

                if movement.quantity < 0:
                    raise ValueError(
                        "A negative movement cannot be "
                        "posted without an existing balance."
                    )

                balance = StockBalance(
                    stock_item_id=movement.stock_item_id,
                    location_id=movement.location_id,
                    quantity=movement.quantity,
                )

                self.balance_repository.add(
                    balance
                )

            else:

                resulting_quantity = (
                    balance.quantity
                    + movement.quantity
                )

                if resulting_quantity < 0:
                    raise ValueError(
                        "Movement would result in "
                        "a negative stock balance."
                    )

                balance.quantity = resulting_quantity

                self.balance_repository.update(
                    balance
                )

            movement.status = "POSTED"
            movement.posted_at = datetime.now(
                timezone.utc
            )

            self.repository.update(
                movement
            )

        return movement


__all__ = [
    "StockMovementService",
]
