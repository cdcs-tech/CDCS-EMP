"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

StockTransfer service tests.
"""

from unittest.mock import Mock

from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import StockTransfer
from app.modules.catering.repositories import StockTransferRepository
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
