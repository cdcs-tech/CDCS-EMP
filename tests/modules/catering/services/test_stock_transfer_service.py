"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

StockTransfer service tests.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.core.crud.transaction import (
    SimpleTransactionManager,
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
from app.modules.catering.services import StockTransferService


def test_service_creates_default_repository():
    """Verify the service creates its default repository."""

    service = StockTransferService()

    assert isinstance(
        service.repository,
        StockTransferRepository,
    )


def test_service_preserves_injected_repository():
    """Verify dependency injection is preserved."""

    repository = Mock(
        spec=StockTransferRepository
    )

    service = StockTransferService(
        repository=repository,
    )

    assert service.repository is repository


def test_paginate_delegates_to_repository():
    """Verify pagination is delegated to the repository."""

    repository = Mock(
        spec=StockTransferRepository
    )

    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=1,
        page_size=25,
    )

    repository.paginate.return_value = expected

    service = StockTransferService(
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
        spec=StockTransferRepository
    )

    transfer = Mock(
        spec=StockTransfer
    )

    repository.get_by_reference.return_value = transfer

    service = StockTransferService(
        repository=repository,
    )

    result = service.get_by_reference(
        "TRF-001"
    )

    assert result is transfer

    repository.get_by_reference.assert_called_once_with(
        "TRF-001"
    )


def _make_transfer(
    *,
    transfer_id=100,
    quantity=Decimal("5.000"),
    source_location_id=1,
    destination_location_id=2,
    status="DRAFT",
):
    """Create a transfer test double with valid posting data."""

    transfer = Mock(
        spec=StockTransfer
    )

    transfer.id = transfer_id
    transfer.stock_item_id = 10
    transfer.source_location_id = source_location_id
    transfer.destination_location_id = destination_location_id
    transfer.quantity = quantity
    transfer.reference = "TRF-001"
    transfer.reason = "Internal stock transfer"
    transfer.status = status
    transfer.occurred_at = datetime(
        2026,
        9,
        5,
        10,
        0,
        tzinfo=timezone.utc,
    )
    transfer.posted_at = None

    return transfer


def _make_balance(
    *,
    quantity=Decimal("10.000"),
    stock_item_id=10,
    location_id=1,
):
    """Create a stock balance test double."""

    balance = Mock(
        spec=StockBalance
    )

    balance.stock_item_id = stock_item_id
    balance.location_id = location_id
    balance.quantity = quantity

    return balance


def _make_service(
    *,
    transfer_repository=None,
    balance_repository=None,
    movement_repository=None,
    transaction_manager=None,
):
    """Create a transfer service with isolated test dependencies."""

    return StockTransferService(
        repository=(
            transfer_repository
            or Mock(
                spec=StockTransferRepository
            )
        ),
        transaction_manager=(
            transaction_manager
            or SimpleTransactionManager()
        ),
        balance_repository=(
            balance_repository
            or Mock(
                spec=StockBalanceRepository
            )
        ),
        movement_repository=(
            movement_repository
            or Mock(
                spec=StockMovementRepository
            )
        ),
    )


def test_post_transfer_updates_source_and_destination_balances():
    """Verify a posted transfer updates both location balances."""

    transfer = _make_transfer()

    transfer_repository = Mock(
        spec=StockTransferRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    movement_repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = SimpleTransactionManager()

    source_balance = _make_balance(
        quantity=Decimal("10.000"),
        location_id=1,
    )

    destination_balance = _make_balance(
        quantity=Decimal("3.000"),
        location_id=2,
    )

    def get_balance(stock_item_id, location_id):
        if location_id == 1:
            return source_balance

        if location_id == 2:
            return destination_balance

        return None

    balance_repository.get_by_stock_item_and_location.side_effect = (
        get_balance
    )

    service = _make_service(
        transfer_repository=transfer_repository,
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        transaction_manager=transaction_manager,
    )

    result = service.post_transfer(
        transfer
    )

    assert result is transfer
    assert source_balance.quantity == Decimal("5.000")
    assert destination_balance.quantity == Decimal("8.000")

    assert transaction_manager.committed is True
    assert transaction_manager.rolled_back is False
    assert transaction_manager.active is False

    assert balance_repository.update.call_count == 2

    transfer_repository.update.assert_called_once_with(
        transfer
    )


def test_post_transfer_creates_destination_balance_when_missing():
    """Verify a destination balance is created when none exists."""

    transfer = _make_transfer(
        quantity=Decimal("4.000")
    )

    transfer_repository = Mock(
        spec=StockTransferRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    movement_repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = SimpleTransactionManager()

    source_balance = _make_balance(
        quantity=Decimal("10.000"),
        location_id=1,
    )

    balance_repository.get_by_stock_item_and_location.side_effect = [
        source_balance,
        None,
    ]

    service = _make_service(
        transfer_repository=transfer_repository,
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        transaction_manager=transaction_manager,
    )

    service.post_transfer(
        transfer
    )

    assert source_balance.quantity == Decimal("6.000")

    balance_repository.add.assert_called_once()

    created_destination_balance = (
        balance_repository.add.call_args.args[0]
    )

    assert isinstance(
        created_destination_balance,
        StockBalance,
    )
    assert created_destination_balance.stock_item_id == 10
    assert created_destination_balance.location_id == 2
    assert created_destination_balance.quantity == 4

    assert transaction_manager.committed is True
    assert transaction_manager.rolled_back is False


def test_post_transfer_rejects_missing_source_balance():
    """Verify a transfer cannot proceed without source stock."""

    transfer = _make_transfer()

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    balance_repository.get_by_stock_item_and_location.return_value = (
        None
    )

    transaction_manager = SimpleTransactionManager()

    service = _make_service(
        balance_repository=balance_repository,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(
        ValueError,
        match="Source balance does not exist",
    ):
        service.post_transfer(
            transfer
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True
    assert transaction_manager.active is False


def test_post_transfer_rejects_insufficient_source_stock():
    """Verify a transfer cannot reduce source stock below zero."""

    transfer = _make_transfer(
        quantity=Decimal("11.000")
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    balance_repository.get_by_stock_item_and_location.return_value = (
        _make_balance(
            quantity=Decimal("10.000"),
            location_id=1,
        )
    )

    transaction_manager = SimpleTransactionManager()

    service = _make_service(
        balance_repository=balance_repository,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(
        ValueError,
        match="Insufficient source stock",
    ):
        service.post_transfer(
            transfer
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True
    assert transaction_manager.active is False


@pytest.mark.parametrize(
    "quantity",
    [
        Decimal("0.000"),
        Decimal("-1.000"),
    ],
)
def test_post_transfer_rejects_non_positive_quantity(
    quantity,
):
    """Verify transfer quantities must be positive."""

    transfer = _make_transfer(
        quantity=quantity
    )

    transaction_manager = SimpleTransactionManager()

    service = _make_service(
        transaction_manager=transaction_manager,
    )

    with pytest.raises(
        ValueError,
        match="Transfer quantity must be greater than zero",
    ):
        service.post_transfer(
            transfer
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is False
    assert transaction_manager.active is False


def test_post_transfer_rejects_same_source_and_destination():
    """Verify source and destination locations must differ."""

    transfer = _make_transfer(
        source_location_id=1,
        destination_location_id=1,
    )

    transaction_manager = SimpleTransactionManager()

    service = _make_service(
        transaction_manager=transaction_manager,
    )

    with pytest.raises(
        ValueError,
        match="Source and destination locations must differ",
    ):
        service.post_transfer(
            transfer
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is False
    assert transaction_manager.active is False


def test_post_transfer_rejects_already_posted_transfer():
    """Verify an already-posted transfer cannot be posted again."""

    transfer = _make_transfer(
        status="POSTED"
    )

    transaction_manager = SimpleTransactionManager()

    service = _make_service(
        transaction_manager=transaction_manager,
    )

    with pytest.raises(
        ValueError,
        match="Transfer is already posted",
    ):
        service.post_transfer(
            transfer
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is False
    assert transaction_manager.active is False


def test_post_transfer_creates_two_transfer_movements():
    """Verify posting creates source and destination movements."""

    transfer = _make_transfer(
        quantity=Decimal("5.000")
    )

    transfer_repository = Mock(
        spec=StockTransferRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    movement_repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = SimpleTransactionManager()

    source_balance = _make_balance(
        quantity=Decimal("10.000"),
        location_id=1,
    )

    destination_balance = _make_balance(
        quantity=Decimal("3.000"),
        location_id=2,
    )

    balance_repository.get_by_stock_item_and_location.side_effect = [
        source_balance,
        destination_balance,
    ]

    service = _make_service(
        transfer_repository=transfer_repository,
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        transaction_manager=transaction_manager,
    )

    service.post_transfer(
        transfer
    )

    assert movement_repository.add.call_count == 2

    created_movements = [
        call.args[0]
        for call in movement_repository.add.call_args_list
    ]

    source_movement = created_movements[0]
    destination_movement = created_movements[1]

    assert isinstance(
        source_movement,
        StockMovement,
    )
    assert isinstance(
        destination_movement,
        StockMovement,
    )

    assert source_movement.stock_item_id == 10
    assert source_movement.location_id == 1
    assert source_movement.quantity == Decimal("-5.000")
    assert source_movement.movement_type == "TRANSFER"
    assert source_movement.status == "POSTED"
    assert source_movement.transfer_id == transfer.id
    assert source_movement.reference == "TRF-001-OUT"

    assert destination_movement.stock_item_id == 10
    assert destination_movement.location_id == 2
    assert destination_movement.quantity == Decimal("5.000")
    assert destination_movement.movement_type == "TRANSFER"
    assert destination_movement.status == "POSTED"
    assert destination_movement.transfer_id == transfer.id
    assert destination_movement.reference == "TRF-001-IN"

    assert (
        source_movement.posted_at
        == destination_movement.posted_at
    )


def test_post_transfer_marks_transfer_posted():
    """Verify successful posting changes status and timestamp."""

    transfer = _make_transfer()

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    balance_repository.get_by_stock_item_and_location.side_effect = [
        _make_balance(
            quantity=Decimal("10.000"),
            location_id=1,
        ),
        _make_balance(
            quantity=Decimal("3.000"),
            location_id=2,
        ),
    ]

    transaction_manager = SimpleTransactionManager()

    service = _make_service(
        balance_repository=balance_repository,
        transaction_manager=transaction_manager,
    )

    result = service.post_transfer(
        transfer
    )

    assert result.status == "POSTED"
    assert result.posted_at is not None
    assert result.posted_at.tzinfo is not None
    assert result.posted_at.utcoffset() is not None

    assert transaction_manager.committed is True


def test_post_transfer_uses_transaction_boundary():
    """Verify successful posting executes inside a transaction."""

    transfer = _make_transfer()

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    balance_repository.get_by_stock_item_and_location.side_effect = [
        _make_balance(
            quantity=Decimal("10.000"),
            location_id=1,
        ),
        _make_balance(
            quantity=Decimal("3.000"),
            location_id=2,
        ),
    ]

    transaction_manager = Mock(
        spec=TransactionManager
    )

    transaction_context = Mock()
    transaction_manager.transaction.return_value.__enter__ = Mock(
        return_value=transaction_context
    )
    transaction_manager.transaction.return_value.__exit__ = Mock(
        return_value=False
    )

    service = _make_service(
        balance_repository=balance_repository,
        transaction_manager=transaction_manager,
    )

    service.post_transfer(
        transfer
    )

    transaction_manager.transaction.assert_called_once_with()

    transaction_manager.transaction.return_value.__enter__.assert_called_once_with()

    transaction_manager.transaction.return_value.__exit__.assert_called_once()


def test_post_transfer_rolls_back_on_failure():
    """Verify a failure during posting rolls back the transaction."""

    transfer = _make_transfer()

    transfer_repository = Mock(
        spec=StockTransferRepository
    )

    balance_repository = Mock(
        spec=StockBalanceRepository
    )

    movement_repository = Mock(
        spec=StockMovementRepository
    )

    transaction_manager = SimpleTransactionManager()

    source_balance = _make_balance(
        quantity=Decimal("10.000"),
        location_id=1,
    )

    destination_balance = _make_balance(
        quantity=Decimal("3.000"),
        location_id=2,
    )

    balance_repository.get_by_stock_item_and_location.side_effect = [
        source_balance,
        destination_balance,
    ]

    movement_repository.add.side_effect = RuntimeError(
        "Movement persistence failed."
    )

    service = _make_service(
        transfer_repository=transfer_repository,
        balance_repository=balance_repository,
        movement_repository=movement_repository,
        transaction_manager=transaction_manager,
    )

    with pytest.raises(
        RuntimeError,
        match="Movement persistence failed",
    ):
        service.post_transfer(
            transfer
        )

    assert transaction_manager.committed is False
    assert transaction_manager.rolled_back is True
    assert transaction_manager.active is False
