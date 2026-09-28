"""
Tests for the Catering Request application service.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import CateringRequest
from app.modules.catering.repositories import CateringRequestRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import CateringRequestService


def test_service_uses_default_repository():
    """Verify the service creates its default repository."""

    service = CateringRequestService()

    assert isinstance(
        service.repository,
        CateringRequestRepository,
    )


def test_service_accepts_injected_repository():
    """Verify dependency injection is preserved."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    service = CateringRequestService(
        repository=repository,
    )

    assert service.repository is repository


def test_service_accepts_injected_authorization_adapter():
    """Verify the authorization adapter is preserved."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    service = CateringRequestService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    assert service.authorization_adapter is authorization_adapter


def test_create_requires_authorization_adapter():
    """Verify protected creation fails closed without an adapter."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    request = Mock(
        spec=CateringRequest,
    )

    service = CateringRequestService(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create(
            request,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_authorizes_before_repository_write():
    """Verify creation uses the canonical Request CREATE permission."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    request = Mock(
        spec=CateringRequest,
    )

    repository.add.return_value = request

    subject = Mock()

    service = CateringRequestService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.create(
        request,
        subject=subject,
    )

    assert result is request

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_REQUEST.CREATE",
    )

    repository.add.assert_called_once_with(
        request,
    )


def test_create_denied_does_not_write_to_repository():
    """Verify denied creation does not mutate the repository."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    request = Mock(
        spec=CateringRequest,
    )

    service = CateringRequestService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.create(
            request,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_update_delegates_to_repository():
    """Verify update is delegated to the repository."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    request = Mock(
        spec=CateringRequest,
    )

    repository.update.return_value = request

    service = CateringRequestService(
        repository=repository,
    )

    result = service.update(
        request,
    )

    assert result is request

    repository.update.assert_called_once_with(
        request,
    )


def test_get_delegates_to_repository():
    """Verify retrieval is delegated to the repository."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    request = Mock(
        spec=CateringRequest,
    )

    repository.get_by_id.return_value = request

    service = CateringRequestService(
        repository=repository,
    )

    result = service.get(
        1,
    )

    assert result is request

    repository.get_by_id.assert_called_once_with(
        1,
    )


def test_get_raises_when_request_does_not_exist():
    """Verify inherited CRUD not-found behavior."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    repository.get_by_id.return_value = None

    service = CateringRequestService(
        repository=repository,
    )

    with pytest.raises(
        EntityNotFoundException,
    ):
        service.get(
            999999,
        )

    repository.get_by_id.assert_called_once_with(
        999999,
    )


def test_delete_delegates_to_repository():
    """Verify deletion is delegated to the repository."""

    repository = Mock(
        spec=CateringRequestRepository,
    )

    request = Mock(
        spec=CateringRequest,
    )

    repository.get_by_id.return_value = request

    service = CateringRequestService(
        repository=repository,
    )

    service.delete(
        1,
    )

    repository.get_by_id.assert_called_once_with(
        1,
    )

    repository.delete.assert_called_once_with(
        request,
    )
