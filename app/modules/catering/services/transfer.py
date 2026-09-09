"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory Services

Stock transfer service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.crud import CRUDService
from app.core.crud.transaction import (
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.data.pagination import PaginatedResult
from app.core.data.query import QueryOptions
from app.modules.catering.models.stock_balance import StockBalance
from app.modules.catering.models.stock_movement import StockMovement
from app.modules.catering.models.stock_transfer import StockTransfer
from app.modules.catering.repositories.balance import StockBalanceRepository
from app.modules.catering.repositories.movement import StockMovementRepository
from app.modules.catering.repositories.transfer import StockTransferRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import StockTransferWorkflow


class StockTransferService(CRUDService[StockTransfer]):
    """
    Service layer for Catering stock transfers.

    Transfer posting is implemented atomically. A posted transfer
    decreases the source balance, increases the destination balance,
    creates the corresponding transfer movements, and becomes
    immutable.

    Workflow lifecycle validation is performed at the service
    boundary. The workflow declares the allowed lifecycle
    transition; the service remains responsible for the actual
    business operation and transaction.
    """

    def __init__(
        self,
        repository: StockTransferRepository | None = None,
        transaction_manager: TransactionManager | None = None,
        balance_repository: StockBalanceRepository | None = None,
        movement_repository: StockMovementRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: StockTransferWorkflow | None = None,
    ) -> None:
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

        self.authorization_adapter = authorization_adapter
        self.workflow = (
            workflow
            or StockTransferWorkflow()
        )

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected stock transfer operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def _validate_workflow_transition(
        self,
        transfer: StockTransfer,
    ) -> None:
        """
        Validate the stock transfer lifecycle transition.

        The workflow validates only the lifecycle transition.
        Business validation, authorization, transaction handling,
        balance updates and persistence remain owned by this service.
        """

        self.workflow.transition(
            transfer.status,
            StockTransferWorkflow.POSTED,
        )

    def create(
        self,
        entity: StockTransfer,
        *,
        subject: Any,
    ) -> StockTransfer:
        """
        Create a stock transfer after authorization.
        """

        self._authorize(
            subject,
            "CATERING.STOCK_TRANSFER.CREATE",
        )

        return super().create(entity)

    def paginate(
        self,
        options: QueryOptions | None = None,
    ) -> PaginatedResult[StockTransfer]:
        """
        Paginate stock transfers.
        """

        return self.repository.paginate(
            options or QueryOptions()
        )

    def get_by_reference(
        self,
        reference: str,
    ) -> StockTransfer | None:
        """
        Retrieve a stock transfer by reference.
        """

        return self.repository.get_by_reference(
            reference
        )

    def post_transfer(
        self,
        transfer: StockTransfer,
        *,
        subject: Any,
    ) -> StockTransfer:
        """
        Post a stock transfer atomically.

        Posting decreases the source stock balance, increases the
        destination balance, creates paired TRANSFER movements,
        and marks the transfer as POSTED.
        """

        self._authorize(
            subject,
            "CATERING.STOCK_TRANSFER.POST",
        )

        if transfer is None:
            raise ValueError(
                "Stock transfer is required."
            )

        if transfer.status == "POSTED":
            raise ValueError(
                "Stock transfer is already posted."
            )

        if transfer.status != "DRAFT":
            raise ValueError(
                "Only draft stock transfers can be posted."
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
                "Source and destination locations "
                "must be different."
            )

        self._validate_workflow_transition(
            transfer
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
                    "Source stock balance does not exist."
                )

            resulting_source_quantity = (
                source_balance.quantity
                - transfer.quantity
            )

            if resulting_source_quantity < 0:
                raise ValueError(
                    "Insufficient stock for transfer."
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
                    location_id=(
                        transfer.destination_location_id
                    ),
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
                    "Destination stock balance "
                    "cannot become negative."
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

            posted_at = datetime.now(
                timezone.utc
            )

            source_movement = StockMovement(
                stock_item_id=transfer.stock_item_id,
                location_id=(
                    transfer.source_location_id
                ),
                movement_type="TRANSFER",
                quantity=-transfer.quantity,
                status="POSTED",
                occurred_at=transfer.occurred_at,
                posted_at=posted_at,
                reference=(
                    f"{transfer.reference}-OUT"
                ),
                reason=transfer.reason,
                transfer_id=transfer.id,
            )

            destination_movement = StockMovement(
                stock_item_id=transfer.stock_item_id,
                location_id=(
                    transfer.destination_location_id
                ),
                movement_type="TRANSFER",
                quantity=transfer.quantity,
                status="POSTED",
                occurred_at=transfer.occurred_at,
                posted_at=posted_at,
                reference=(
                    f"{transfer.reference}-IN"
                ),
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
            transfer.posted_at = posted_at

            self.repository.update(
                transfer
            )

        return transfer


__all__ = [
    "StockTransferService",
]
