"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock transfer service.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.core.crud import CRUDService
from app.core.crud.transaction import (
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import (
    StockBalance,
    StockMovement,
    StockTransfer,
)
from app.modules.catering.repositories import (
    StockBalanceRepository,
    StockMovementRepository,
    StockTransferRepository,
)


class StockTransferService(
    CRUDService[StockTransfer],
):
    """
    Application service for Catering StockTransfer entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, transfer-specific retrieval operations,
    and atomic inventory transfer posting.

    Transfer posting coordinates source and destination
    StockBalance updates together with the immutable transfer
    movement records inside one enterprise transaction.
    """

    def __init__(
        self,
        repository: StockTransferRepository | None = None,
        transaction_manager: TransactionManager | None = None,
        balance_repository: StockBalanceRepository | None = None,
        movement_repository: StockMovementRepository | None = None,
    ) -> None:
        """
        Initialize the StockTransfer service.

        Args:
            repository:
                Optional StockTransfer repository.

            transaction_manager:
                Optional enterprise transaction manager.

            balance_repository:
                Optional StockBalance repository.

            movement_repository:
                Optional StockMovement repository.
        """

        super().__init__(
            repository
            or StockTransferRepository(),
            entity_name="StockTransfer",
        )

        self.transaction_manager = (
            transaction_manager
            or SQLAlchemyTransactionManager()
        )

        self.balance_repository = (
            balance_repository
            or StockBalanceRepository()
        )

        self.movement_repository = (
            movement_repository
            or StockMovementRepository()
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[StockTransfer]:
        """
        Return a paginated StockTransfer result.
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
        """

        return self.repository.get_by_reference(
            reference
        )

    def post_transfer(
        self,
        transfer: StockTransfer,
    ) -> StockTransfer:
        """
        Post a stock transfer atomically.

        The operation decreases the source balance,
        increases the destination balance, creates the two
        corresponding TRANSFER movements, and marks the
        transfer as POSTED within one transaction.

        Raises:
            ValueError:
                If the transfer is invalid, already posted,
                has insufficient source stock, or would produce
                an invalid inventory state.
        """

        if transfer is None:
            raise ValueError(
                "Transfer is required."
            )

        if transfer.status == "POSTED":
            raise ValueError(
                "Transfer is already posted."
            )

        if transfer.status != "DRAFT":
            raise ValueError(
                "Only DRAFT transfers can be posted."
            )

        if transfer.quantity is None:
            raise ValueError(
                "Transfer quantity is required."
            )

        if transfer.quantity <= 0:
            raise ValueError(
                "Transfer quantity must be greater than zero."
            )

        if transfer.stock_item_id is None:
            raise ValueError(
                "Stock item is required."
            )

        if transfer.source_location_id is None:
            raise ValueError(
                "Source location is required."
            )

        if transfer.destination_location_id is None:
            raise ValueError(
                "Destination location is required."
            )

        if (
            transfer.source_location_id
            == transfer.destination_location_id
        ):
            raise ValueError(
                "Source and destination locations must differ."
            )

        with self.transaction_manager.transaction():
            source_balance = (
                self.balance_repository
                .get_by_stock_item_and_location(
                    transfer.stock_item_id,
                    transfer.source_location_id,
                )
            )

            if source_balance is None:
                raise ValueError(
                    "Source balance does not exist."
                )

            resulting_source_quantity = (
                source_balance.quantity
                - transfer.quantity
            )

            if resulting_source_quantity < 0:
                raise ValueError(
                    "Insufficient source stock."
                )

            destination_balance = (
                self.balance_repository
                .get_by_stock_item_and_location(
                    transfer.stock_item_id,
                    transfer.destination_location_id,
                )
            )

            if destination_balance is None:
                destination_balance = StockBalance(
                    stock_item_id=transfer.stock_item_id,
                    location_id=transfer.destination_location_id,
                    quantity=0,
                )

                self.balance_repository.add(
                    destination_balance
                )

            resulting_destination_quantity = (
                destination_balance.quantity
                + transfer.quantity
            )

            if resulting_destination_quantity < 0:
                raise ValueError(
                    "Destination balance cannot be negative."
                )

            source_balance.quantity = (
                resulting_source_quantity
            )

            destination_balance.quantity = (
                resulting_destination_quantity
            )

            self.balance_repository.update(
                source_balance
            )

            self.balance_repository.update(
                destination_balance
            )

            now = datetime.now(
                timezone.utc
            )

            source_movement = StockMovement(
                stock_item_id=transfer.stock_item_id,
                location_id=transfer.source_location_id,
                quantity=-transfer.quantity,
                movement_type="TRANSFER",
                status="POSTED",
                occurred_at=transfer.occurred_at,
                posted_at=now,
                reference=f"{transfer.reference}-OUT",
                reason=transfer.reason,
                transfer_id=transfer.id,
            )

            destination_movement = StockMovement(
                stock_item_id=transfer.stock_item_id,
                location_id=transfer.destination_location_id,
                quantity=transfer.quantity,
                movement_type="TRANSFER",
                status="POSTED",
                occurred_at=transfer.occurred_at,
                posted_at=now,
                reference=f"{transfer.reference}-IN",
                reason=transfer.reason,
                transfer_id=transfer.id,
            )

            self.movement_repository.add(
                source_movement
            )

            self.movement_repository.add(
                destination_movement
            )

            transfer.status = "POSTED"
            transfer.posted_at = now

            self.repository.update(
                transfer
            )

        return transfer


__all__ = [
    "StockTransferService",
]
