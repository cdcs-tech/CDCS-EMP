"""
Tests for the Catering Event application service.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import CateringEvent
from app.modules.catering.repositories import CateringEventRepository
from app.modules.catering.services import CateringEventService


def test_service_uses_default_repository():
    service = CateringEventService()

    assert isinstance(
        service.repository,
        CateringEventRepository,
    )


def test_service_accepts_injected_repository():
    repository = Mock(
        spec=CateringEventRepository
    )

    service = CateringEventService(
        repository=repository
    )

    assert service.repository is repository


def test_create_delegates_to_repository():
    repository = Mock(
        spec=CateringEventRepository
    )

    event = Mock(
        spec=CateringEvent
    )

    repository.add.return_value = event

    service = CateringEventService(
        repository=repository
    )

    result = service.create(
        event
    )

    assert result is event
    repository.add.assert_called_once_with(
        event
    )


def test_update_delegates_to_repository():
    repository = Mock(
        spec=CateringEventRepository
    )

    event = Mock(
        spec=CateringEvent
    )

    repository.update.return_value = event

    service = CateringEventService(
        repository=repository
    )

    result = service.update(
        event
    )

    assert result is event
    repository.update.assert_called_once_with(
        event
    )


def test_get_delegates_to_repository():
    repository = Mock(
        spec=CateringEventRepository
    )

    event = Mock(
        spec=CateringEvent
    )

    repository.get_by_id.return_value = event

    service = CateringEventService(
        repository=repository
    )

    result = service.get(
        1
    )

    assert result is event
    repository.get_by_id.assert_called_once_with(
        1
    )


def test_get_raises_when_event_does_not_exist():
    repository = Mock(
        spec=CateringEventRepository
    )

    repository.get_by_id.return_value = None

    service = CateringEventService(
        repository=repository
    )

    with pytest.raises(
        EntityNotFoundException
    ):
        service.get(
            999999
        )

    repository.get_by_id.assert_called_once_with(
        999999
    )


def test_delete_delegates_to_repository():
    repository = Mock(
        spec=CateringEventRepository
    )

    event = Mock(
        spec=CateringEvent
    )

    repository.get_by_id.return_value = event

    service = CateringEventService(
        repository=repository
    )

    service.delete(
        1
    )

    repository.get_by_id.assert_called_once_with(
        1
    )

    repository.delete.assert_called_once_with(
        event
    )
