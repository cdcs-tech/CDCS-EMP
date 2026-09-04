"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

InventoryLocation service tests.
"""

from unittest.mock import Mock

from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import InventoryLocation
from app.modules.catering.repositories import (
    InventoryLocationRepository,
)
from app.modules.catering.services import (
    InventoryLocationService,
)


def test_service_creates_default_repository():
    """Verify the service creates its default repository."""

    service = InventoryLocationService()

    assert isinstance(
        service.repository,
        InventoryLocationRepository,
    )


def test_service_preserves_injected_repository():
    """Verify dependency injection is preserved."""

    repository = Mock(
        spec=InventoryLocationRepository
    )

    service = InventoryLocationService(
        repository=repository,
    )

    assert service.repository is repository


def test_paginate_delegates_to_repository():
    """Verify pagination is delegated to the repository."""

    repository = Mock(
        spec=InventoryLocationRepository
    )

    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=1,
        page_size=25,
    )

    repository.paginate.return_value = expected

    service = InventoryLocationService(
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


def test_get_by_code_delegates_to_repository():
    """Verify code-specific retrieval delegation."""

    repository = Mock(
        spec=InventoryLocationRepository
    )

    location = Mock(
        spec=InventoryLocation
    )

    repository.get_by_code.return_value = location

    service = InventoryLocationService(
        repository=repository,
    )

    result = service.get_by_code(
        "MAIN"
    )

    assert result is location

    repository.get_by_code.assert_called_once_with(
        "MAIN"
    )
