"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

StockMovement service tests.
"""

import pytest
from unittest.mock import Mock

from app.core.crud import (
    SimpleTransactionManager,
    SQLAlchemyTransactionManager,
    TransactionManager,
)
from app.core.data import PaginatedResult, QueryOptions
from app.modules.catering.models import StockMovement
from app.modules.catering.repositories import StockMovementRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import StockMovementService


TEST_SUBJECT = "test-user"


def _allow_authorization():
    """Create an authorization adapter that allows the requested permission."""

    return CateringAuthorizationAdapter(
        evaluator=lambda subject, permission: True,
    )


def _deny_authorization():
    """Create an authorization adapter that denies the requested permission."""

    return CateringAuthorizationAdapter(
        evaluator=lambda subject, permission: False,
    )


def _recording_authorization():
    """Create an authorization adapter that records authorization requests."""

    evaluator = Mock(
        return_value=True
    )

    adapter = CateringAuthorizationAdapter(
        evaluator=evaluator,
    )

    return adapter, evaluator


def test_service_creates_default_repository():
    """Verify the service creates its default repository."""

    service = StockMovementService()

    assert isinstance(
        service.repository,
        StockMovementRepository,
    )


def test_service_preserves_injected_repository():
    """Verify dependency injection is preserved."""

    repository = Mock(
        spec=StockMovementRepository
    )

    service = StockMovementService(
        repository=repository,
    )

    assert service.repository is repository


def test_paginate_delegates_to_repository():
    """Verify pagination is delegated to the repository."""

    repository = Mock(
        spec=StockMovementRepository
    )

    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=1,
        page_size=25,
    )

    repository.paginate.return_value = expected

    service = StockMovementService(
        repository=repository,
    )

    options = QueryOptions()

    result = service.paginate(
        options
    )

    assert result is expected

    repository.paginate.assert_called_once_with(
        options
    )


def test_get_by_reference_delegates_to_repository():
    """Verify reference-specific retrieval delegation."""

    repository = Mock(
        spec=StockMovementRepository
    )

    movement = Mock(
        spec=StockMovement
    )

    repository.get_by_reference.return_value = movement

    service = StockMovementService(
        repository=repository,
    )

    result = service.get_by_reference(
        "MOV-001"
    )

    assert result is movement

    repository.get_by_reference.assert_called_once_with(
        "MOV-001"
    )


def test_service_creates_default_transaction_manager():
    """Verify the service creates its default transaction manager."""

    service = StockMovementService()

    assert isinstance(
        service.transaction_manager,
        SQLAlchemyTransactionManager,
    )


def test_service_preserves_injected_transaction_manager():
    """Verify transaction-manager dependency injection is preserved."""

    repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = Mock(
        spec=TransactionManager
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
    )

    assert service.repository is repository
    assert service.transaction_manager is transaction_manager


def test_service_preserves_injected_authorization_adapter():
    """Verify authorization dependency injection is preserved."""

    repository = Mock(
        spec=StockMovementRepository
    )

    authorization_adapter = _allow_authorization()

    service = StockMovementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    assert service.authorization_adapter is authorization_adapter


def test_create_authorizes_before_repository_mutation():
    """Verify movement creation requires the CREATE permission."""

    repository = Mock(
        spec=StockMovementRepository
    )

    movement = Mock(
        spec=StockMovement
    )

    authorization_adapter, evaluator = (
        _recording_authorization()
    )

    repository.add.return_value = movement

    service = StockMovementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.create(
        movement,
        subject=TEST_SUBJECT,
    )

    assert result is movement

    evaluator.assert_called_once_with(
        TEST_SUBJECT,
        "CATERING.STOCK_MOVEMENT.CREATE",
    )

    repository.add.assert_called_once_with(
        movement
    )


def test_create_denied_does_not_mutate_repository():
    """Verify denied movement creation never reaches the repository."""

    repository = Mock(
        spec=StockMovementRepository
    )

    movement = Mock(
        spec=StockMovement
    )

    service = StockMovementService(
        repository=repository,
        authorization_adapter=_deny_authorization(),
    )

    with pytest.raises(Exception):
        service.create(
            movement,
            subject=TEST_SUBJECT,
        )

    repository.add.assert_not_called()


def test_post_movement_updates_existing_balance():
    """Verify posting updates an existing stock balance."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "RECEIPT"
    movement.quantity = 5
    movement.stock_item_id = 1
    movement.location_id = 1

    balance = Mock()
    balance.quantity = 10

    balance_repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
    )

    result = service.post_movement(
        movement,
        subject=TEST_SUBJECT,
    )

    assert result is movement
    assert balance.quantity == 15
    assert movement.status == "POSTED"
    assert movement.posted_at is not None

    balance_repository.update.assert_called_once_with(
        balance
    )

    repository.update.assert_called_once_with(
        movement
    )

    assert transaction_manager.committed is True
    assert transaction_manager.rolled_back is False


def test_post_movement_creates_balance_for_positive_movement():
    """Verify a positive movement creates a missing balance."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "RECEIPT"
    movement.quantity = 10
    movement.stock_item_id = 1
    movement.location_id = 1

    balance_repository.get_by_stock_item_and_location.return_value = (
        None
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
    )

    result = service.post_movement(
        movement,
        subject=TEST_SUBJECT,
    )

    assert result is movement
    assert movement.status == "POSTED"
    assert movement.posted_at is not None

    balance_repository.add.assert_called_once()

    created_balance = (
        balance_repository.add.call_args.args[0]
    )

    assert created_balance.stock_item_id == 1
    assert created_balance.location_id == 1
    assert created_balance.quantity == 10

    assert transaction_manager.committed is True
    assert transaction_manager.rolled_back is False


def test_post_movement_rejects_negative_movement_without_balance():
    """Verify a negative movement cannot create a missing balance."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "ISSUE"
    movement.quantity = -5
    movement.stock_item_id = 1
    movement.location_id = 1

    balance_repository.get_by_stock_item_and_location.return_value = (
        None
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
    )

    with pytest.raises(ValueError):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    balance_repository.add.assert_not_called()
    repository.update.assert_not_called()

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True


def test_post_movement_rejects_negative_resulting_balance():
    """Verify posting cannot produce a negative stock balance."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "ISSUE"
    movement.quantity = -5
    movement.stock_item_id = 1
    movement.location_id = 1

    balance = Mock()
    balance.quantity = 3

    balance_repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
    )

    with pytest.raises(ValueError):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    assert balance.quantity == 3
    balance_repository.update.assert_not_called()
    repository.update.assert_not_called()

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True


def test_post_movement_rejects_already_posted_movement():
    """Verify a posted movement cannot be posted again."""

    repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = Mock(
        spec=TransactionManager
    )

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "POSTED"

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        authorization_adapter=_allow_authorization(),
    )

    with pytest.raises(ValueError):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    transaction_manager.transaction.assert_not_called()
    repository.update.assert_not_called()


def test_post_movement_rejects_zero_quantity():
    """Verify zero-quantity movements cannot be posted."""

    repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = Mock(
        spec=TransactionManager
    )

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "RECEIPT"
    movement.quantity = 0

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        authorization_adapter=_allow_authorization(),
    )

    with pytest.raises(ValueError):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    transaction_manager.transaction.assert_not_called()
    repository.update.assert_not_called()


def test_post_movement_authorizes_post_operation():
    """Verify posting requests the POST permission."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "RECEIPT"
    movement.quantity = 5
    movement.stock_item_id = 1
    movement.location_id = 1

    balance = Mock()
    balance.quantity = 10

    balance_repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    authorization_adapter, evaluator = (
        _recording_authorization()
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=authorization_adapter,
    )

    service.post_movement(
        movement,
        subject=TEST_SUBJECT,
    )

    evaluator.assert_called_once_with(
        TEST_SUBJECT,
        "CATERING.STOCK_MOVEMENT.POST",
    )


def test_post_movement_denied_does_not_enter_transaction():
    """Verify denied posting stops before transaction or persistence."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = Mock(
        spec=TransactionManager
    )

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "RECEIPT"
    movement.quantity = 5
    movement.stock_item_id = 1
    movement.location_id = 1

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_deny_authorization(),
    )

    with pytest.raises(Exception):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    transaction_manager.transaction.assert_not_called()
    balance_repository.get_by_stock_item_and_location.assert_not_called()
    balance_repository.add.assert_not_called()
    balance_repository.update.assert_not_called()
    repository.update.assert_not_called()


def test_post_movement_uses_transaction_boundary():
    """Verify posting executes through the transaction manager."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "RECEIPT"
    movement.quantity = 5
    movement.stock_item_id = 1
    movement.location_id = 1

    balance = Mock()
    balance.quantity = 10

    balance_repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
    )

    service.post_movement(
        movement,
        subject=TEST_SUBJECT,
    )

    assert transaction_manager.committed is True
    assert transaction_manager.rolled_back is False
    assert transaction_manager.active is False


def test_post_movement_rolls_back_on_failure():
    """Verify transaction rollback occurs when posting fails."""

    repository = Mock(
        spec=StockMovementRepository
    )

    balance_repository = Mock()
    transaction_manager = SimpleTransactionManager()

    movement = Mock(
        spec=StockMovement
    )

    movement.status = "DRAFT"
    movement.movement_type = "ISSUE"
    movement.quantity = -5
    movement.stock_item_id = 1
    movement.location_id = 1

    balance = Mock()
    balance.quantity = 3

    balance_repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    service = StockMovementService(
        repository=repository,
        transaction_manager=transaction_manager,
        balance_repository=balance_repository,
        authorization_adapter=_allow_authorization(),
    )

    with pytest.raises(ValueError):
        service.post_movement(
            movement,
            subject=TEST_SUBJECT,
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True
    assert transaction_manager.active is False

    repository.update.assert_not_called()
