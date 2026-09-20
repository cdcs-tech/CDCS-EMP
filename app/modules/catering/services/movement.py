"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory Services

Stock movement service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.crud import CRUDService
from app.core.crud.transaction import (
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.data.pagination import PaginatedResult
from app.core.data.query import QueryOptions
from app.modules.catering.models.inventory_receipt_idempotency import (
    InventoryReceiptIdempotency,
)
from app.modules.catering.models.stock_balance import StockBalance
from app.modules.catering.models.stock_movement import StockMovement
from app.modules.catering.repositories.balance import StockBalanceRepository
from app.modules.catering.repositories.inventory_receipt_idempotency import (
    InventoryReceiptIdempotencyRepository,
)
from app.modules.catering.repositories.movement import StockMovementRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import StockMovementWorkflow


class StockMovementService(CRUDService[StockMovement]):
    """
    Service layer for Catering stock movements.

    Movement posting is implemented atomically. A posted movement
    updates the authoritative StockBalance and becomes immutable.
    Operational actions are protected through the Catering
    authorization adapter.

    Workflow lifecycle validation is performed at the service
    boundary. The workflow declares the allowed lifecycle
    transition; the service remains responsible for the actual
    business operation and transaction.
    """

    def __init__(
        self,
        repository: StockMovementRepository | None = None,
        transaction_manager: TransactionManager | None = None,
        balance_repository: StockBalanceRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: StockMovementWorkflow | None = None,
        idempotency_repository: (
            InventoryReceiptIdempotencyRepository | None
        ) = None,
    ) -> None:
        super().__init__(
            repository
            or StockMovementRepository(),
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

        self.authorization_adapter = authorization_adapter

        self.workflow = (
            workflow
            or StockMovementWorkflow()
        )

        self.idempotency_repository = (
            idempotency_repository
            or InventoryReceiptIdempotencyRepository()
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
                "for protected stock movement operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def _validate_workflow_transition(
        self,
        movement: StockMovement,
    ) -> None:
        """
        Validate the stock movement lifecycle transition.
        """

        self.workflow.transition(
            movement.status,
            StockMovementWorkflow.POSTED,
        )

    def _validate_movement_for_posting(
        self,
        movement: StockMovement,
    ) -> None:
        """
        Validate the business conditions required to post
        a stock movement.
        """

        if movement is None:
            raise ValueError(
                "Stock movement is required."
            )

        if movement.status == "POSTED":
            raise ValueError(
                "Stock movement is already posted."
            )

        if movement.movement_type not in {
            "OPENING_BALANCE",
            "RECEIPT",
            "ISSUE",
            "ADJUSTMENT",
            "TRANSFER",
        }:
            raise ValueError(
                "Invalid stock movement type."
            )

        if movement.quantity == 0:
            raise ValueError(
                "Stock movement quantity cannot be zero."
            )

        if movement.stock_item_id is None:
            raise ValueError(
                "Stock item is required."
            )

        if movement.location_id is None:
            raise ValueError(
                "Inventory location is required."
            )

        self._validate_workflow_transition(
            movement
        )

    def _apply_balance_effect(
        self,
        movement: StockMovement,
    ) -> None:
        """
        Apply the physical StockBalance effect.

        This method must execute inside an existing Inventory
        transaction boundary.
        """

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
                    "Cannot post a negative movement "
                    "without an existing stock balance."
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
                    "Stock balance cannot become negative."
                )

            balance.quantity = resulting_quantity

            self.balance_repository.update(
                balance
            )

    def create(
        self,
        entity: StockMovement,
        *,
        subject: Any,
    ) -> StockMovement:
        """
        Create a stock movement after authorization.
        """

        self._authorize(
            subject,
            "CATERING.STOCK_MOVEMENT.CREATE",
        )

        return super().create(entity)

    def paginate(
        self,
        options: QueryOptions | None = None,
    ) -> PaginatedResult[StockMovement]:
        """
        Paginate stock movements.
        """

        return self.repository.paginate(
            options or QueryOptions()
        )

    def get_by_reference(
        self,
        reference: str,
    ) -> StockMovement | None:
        """
        Retrieve a stock movement by reference.
        """

        return self.repository.get_by_reference(
            reference
        )

    def post_movement(
        self,
        movement: StockMovement,
        *,
        subject: Any,
    ) -> StockMovement:
        """
        Post a stock movement atomically.

        Posting updates the authoritative stock balance and marks
        the movement as POSTED. Draft movements do not affect stock.
        """

        self._authorize(
            subject,
            "CATERING.STOCK_MOVEMENT.POST",
        )

        self._validate_movement_for_posting(
            movement
        )

        with self.transaction_manager.transaction():
            self._apply_balance_effect(
                movement
            )

            movement.status = "POSTED"

            movement.posted_at = datetime.now(
                timezone.utc
            )

            self.repository.update(
                movement
            )

        return movement

    def post_receipt_movement(
        self,
        movement: StockMovement,
        *,
        subject: Any,
        idempotency_key: str,
    ) -> StockMovement:
        """
        Post an Inventory purchase-order receipt atomically.

        The idempotency record, StockMovement and StockBalance
        effect are committed as one Inventory transaction.

        A previously successful idempotency key returns the
        originally posted StockMovement without applying another
        physical stock effect.

        A concurrent duplicate is protected by the database-level
        unique constraint on InventoryReceiptIdempotency.
        """

        self._authorize(
            subject,
            "CATERING.STOCK_MOVEMENT.POST",
        )

        if not isinstance(
            idempotency_key,
            str,
        ):
            raise ValueError(
                "Inventory receipt idempotency key is required."
            )

        normalized_idempotency_key = (
            idempotency_key.strip()
        )

        if not normalized_idempotency_key:
            raise ValueError(
                "Inventory receipt idempotency key is required."
            )

        self._validate_movement_for_posting(
            movement
        )

        try:
            with self.transaction_manager.transaction():
                existing = (
                    self.idempotency_repository
                    .get_by_idempotency_key(
                        normalized_idempotency_key
                    )
                )

                if existing is not None:
                    return existing.stock_movement

                self.repository.add(
                    movement
                )

                self._apply_balance_effect(
                    movement
                )

                movement.status = "POSTED"

                movement.posted_at = datetime.now(
                    timezone.utc
                )

                self.repository.update(
                    movement
                )

                idempotency_record = (
                    InventoryReceiptIdempotency(
                        idempotency_key=(
                            normalized_idempotency_key
                        ),
                        stock_movement_id=movement.id,
                        stock_movement=movement,
                    )
                )

                self.idempotency_repository.add(
                    idempotency_record
                )

            return movement

        except IntegrityError:
            existing = (
                self.idempotency_repository
                .get_by_idempotency_key(
                    normalized_idempotency_key
                )
            )

            if existing is not None:
                return existing.stock_movement

            raise


__all__ = [
    "StockMovementService",
]
