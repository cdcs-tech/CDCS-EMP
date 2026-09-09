"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory Workflow Enforcement Tests
"""

from unittest.mock import Mock

import pytest

from app.core.crud import SimpleTransactionManager
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
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import (
    StockMovementService,
    StockTransferService,
)
from app.modules.catering.workflows import (
    StockMovementWorkflow,
    StockTransferWorkflow,
)


TEST_SUBJECT = "test-user"


def _allow_authorization():
    """Create an authorization adapter that allows operations."""

    return CateringAuthorizationAdapter(
        evaluator=lambda subject, permission: True,
    )


def test_stock_movement_service_enforces_workflow_transition():
    """
    Stock Movement posting must consult the workflow before
    entering the transaction boundary.
    """

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    balance = Mock(
        spec=StockBalance
    )
    balance.quantity = 10

    balance_repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    workflow = Mock(
        spec=StockMovementWorkflow
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=SimpleTransactionManager(),
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
        workflow=workflow,
    )

    movement = Mock(
        spec=StockMovement
    )

    movement.status = StockMovementWorkflow.DRAFT
    movement.movement_type = "RECEIPT"
    movement.quantity = 5
    movement.stock_item_id = 1
    movement.location_id = 1

    service.post_movement(
        movement,
        subject=TEST_SUBJECT,
    )

    workflow.transition.assert_called_once_with(
        StockMovementWorkflow.DRAFT,
        StockMovementWorkflow.POSTED,
    )


def test_stock_movement_service_rejects_invalid_workflow_transition():
    """
    Stock Movement posting must stop when the workflow rejects
    the requested lifecycle transition.
    """

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    workflow = Mock(
        spec=StockMovementWorkflow
    )

    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition: CANCELLED -> POSTED"
    )

    transaction_manager = Mock(
        spec=SimpleTransactionManager
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
        workflow=workflow,
    )

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "CANCELLED"
    movement.movement_type = "RECEIPT"
    movement.quantity = 5
    movement.stock_item_id = 1
    movement.location_id = 1

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    workflow.transition.assert_called_once_with(
        "CANCELLED",
        StockMovementWorkflow.POSTED,
    )

    transaction_manager.transaction.assert_not_called()
    balance_repository.get_by_stock_item_and_location.assert_not_called()
    repository.update.assert_not_called()


def test_stock_transfer_service_enforces_workflow_transition():
    """
    Stock Transfer posting must consult the workflow before
    entering the transaction boundary.
    """

    repository = Mock(
        spec=StockTransferRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    movement_repository = Mock(
        spec=StockMovementRepository
    )

    source_balance = Mock(
        spec=StockBalance
    )
    source_balance.quantity = 20

    destination_balance = Mock(
        spec=StockBalance
    )
    destination_balance.quantity = 5

    balance_repository.get_by_stock_item_and_location.side_effect = [
        source_balance,
        destination_balance,
    ]

    workflow = Mock(
        spec=StockTransferWorkflow
    )

    service = StockTransferService(
        repository=repository,
        transaction_manager=SimpleTransactionManager(),
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        authorization_adapter=_allow_authorization(),
        workflow=workflow,
    )

    transfer = Mock(
        spec=StockTransfer
    )

    transfer.status = StockTransferWorkflow.DRAFT
    transfer.quantity = 5
    transfer.stock_item_id = 1
    transfer.source_location_id = 1
    transfer.destination_location_id = 2
    transfer.reference = "OW-2.5-TRF-001"
    transfer.reason = "Workflow enforcement test"
    transfer.occurred_at = None
    transfer.id = 1

    service.post_transfer(
        transfer,
        subject=TEST_SUBJECT,
    )

    workflow.transition.assert_called_once_with(
        StockTransferWorkflow.DRAFT,
        StockTransferWorkflow.POSTED,
    )


def test_stock_transfer_service_rejects_invalid_workflow_transition():
    """
    Stock Transfer posting must stop when the workflow rejects
    the requested lifecycle transition.
    """

    repository = Mock(
        spec=StockTransferRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    movement_repository = Mock(
        spec=StockMovementRepository
    )

    workflow = Mock(
        spec=StockTransferWorkflow
    )

    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition: CANCELLED -> POSTED"
    )

    transaction_manager = Mock(
        spec=SimpleTransactionManager
    )

    service = StockTransferService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        authorization_adapter=_allow_authorization(),
        workflow=workflow,
    )

    transfer = Mock(
        spec=StockTransfer
    )

    transfer.status = "CANCELLED"
    transfer.quantity = 5
    transfer.stock_item_id = 1
    transfer.source_location_id = 1
    transfer.destination_location_id = 2

    with pytest.raises(
        ValueError,
        match="Only draft stock transfers can be posted",
    ):
        service.post_transfer(
            transfer,
            subject=TEST_SUBJECT,
        )

    workflow.transition.assert_not_called()
    transaction_manager.transaction.assert_not_called()
    balance_repository.get_by_stock_item_and_location.assert_not_called()
    movement_repository.add.assert_not_called()
    repository.update.assert_not_called()
