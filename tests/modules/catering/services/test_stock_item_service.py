"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

StockItem service tests.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockItem
from app.modules.catering.repositories import StockItemRepository
from app.modules.catering.services import StockItemService


def test_service_creates_default_repository():
    """Verify the service creates its default repository."""

    service = StockItemService()

    assert isinstance(
        service.repository,
        StockItemRepository,
    )


def test_service_preserves_injected_repository():
    """Verify dependency injection is preserved."""

    repository = Mock(spec=StockItemRepository)

    service = StockItemService(
        repository=repository,
    )

    assert service.repository is repository


def test_paginate_delegates_to_repository():
    """Verify pagination is delegated to the repository."""

    repository = Mock(spec=StockItemRepository)
    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=1,
        page_size=25,
    )
    repository.paginate.return_value = expected

    service = StockItemService(
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


def test_get_by_product_id_delegates_to_repository():
    """Verify Product-specific retrieval delegation."""

    repository = Mock(spec=StockItemRepository)
    stock_item = Mock(spec=StockItem)
    repository.get_by_product_id.return_value = stock_item

    service = StockItemService(
        repository=repository,
    )

    result = service.get_by_product_id(
        10
    )

    assert result is stock_item
    repository.get_by_product_id.assert_called_once_with(
        10
    )


def test_exists_for_product_delegates_to_repository():
    """Verify StockItem existence delegation."""

    repository = Mock(spec=StockItemRepository)
    repository.exists_for_product.return_value = True

    service = StockItemService(
        repository=repository,
    )

    result = service.exists_for_product(
        10
    )

    assert result is True
    repository.exists_for_product.assert_called_once_with(
        10
    )


def test_get_raises_when_stock_item_does_not_exist():
    """Verify inherited CRUD not-found behavior."""

    repository = Mock(spec=StockItemRepository)
    repository.get_by_id.return_value = None

    service = StockItemService(
        repository=repository,
    )

    with pytest.raises(
        EntityNotFoundException
    ):
        service.get(
            999
        )

    repository.get_by_id.assert_called_once_with(
        999
    )
