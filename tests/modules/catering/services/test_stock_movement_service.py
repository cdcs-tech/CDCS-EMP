"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

StockMovement service tests.
"""

from unittest.mock import Mock

from app.core.crud import (
    SQLAlchemyTransactionManager,
    TransactionManager,
)

from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockMovement
from app.modules.catering.repositories import StockMovementRepository
from app.modules.catering.services import StockMovementService


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
