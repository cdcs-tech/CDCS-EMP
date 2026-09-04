"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

StockBalance service tests.
"""

from unittest.mock import Mock

from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockBalance
from app.modules.catering.repositories import StockBalanceRepository
from app.modules.catering.services import StockBalanceService


def test_service_creates_default_repository():
    """Verify the service creates its default repository."""

    service = StockBalanceService()

    assert isinstance(
        service.repository,
        StockBalanceRepository,
    )


def test_service_preserves_injected_repository():
    """Verify dependency injection is preserved."""

    repository = Mock(
        spec=StockBalanceRepository
    )

    service = StockBalanceService(
        repository=repository,
    )

    assert service.repository is repository


def test_paginate_delegates_to_repository():
    """Verify pagination is delegated to the repository."""

    repository = Mock(
        spec=StockBalanceRepository
    )

    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=1,
        page_size=25,
    )

    repository.paginate.return_value = expected

    service = StockBalanceService(
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


def test_get_by_stock_item_and_location_delegates():
    """Verify StockItem/location balance retrieval delegation."""

    repository = Mock(
        spec=StockBalanceRepository
    )

    balance = Mock(
        spec=StockBalance
    )

    repository.get_by_stock_item_and_location.return_value = (
        balance
    )

    service = StockBalanceService(
        repository=repository,
    )

    result = service.get_by_stock_item_and_location(
        10,
        20,
    )

    assert result is balance

    repository.get_by_stock_item_and_location.assert_called_once_with(
        10,
        20,
    )


def test_get_by_stock_item_delegates():
    """Verify StockItem balance retrieval delegation."""

    repository = Mock(
        spec=StockBalanceRepository
    )

    balances = [
        Mock(spec=StockBalance),
        Mock(spec=StockBalance),
    ]

    repository.get_by_stock_item.return_value = balances

    service = StockBalanceService(
        repository=repository,
    )

    result = service.get_by_stock_item(
        10
    )

    assert result is balances

    repository.get_by_stock_item.assert_called_once_with(
        10
    )


def test_get_by_location_delegates():
    """Verify location balance retrieval delegation."""

    repository = Mock(
        spec=StockBalanceRepository
    )

    balances = [
        Mock(spec=StockBalance),
    ]

    repository.get_by_location.return_value = balances

    service = StockBalanceService(
        repository=repository,
    )

    result = service.get_by_location(
        20
    )

    assert result is balances

    repository.get_by_location.assert_called_once_with(
        20
    )
