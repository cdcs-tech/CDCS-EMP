"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Tests for Catering Request -> Event coordination.
"""

from datetime import date
from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import (
    EntityNotFoundException,
)
from app.modules.catering.models import CateringEvent, CateringRequest
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringRequestRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.security.permissions import CATERING_EVENT_CREATE
from app.modules.catering.services import (
    CateringRequestEventCoordinationService,
)


def _build_request() -> CateringRequest:
    return CateringRequest(
        id=17,
        customer_id=42,
        request_date=date(2026, 10, 6),
        requested_service="Corporate Catering",
        service_date=date(2026, 10, 10),
        attendance=75,
        requirements="Buffet service and beverages",
        notes="Client prefers morning setup",
        status="SUBMITTED",
    )


def test_service_uses_default_repositories():
    service = CateringRequestEventCoordinationService()

    assert isinstance(
        service.request_repository,
        CateringRequestRepository,
    )
    assert isinstance(
        service.event_repository,
        CateringEventRepository,
    )


def test_create_event_requires_authorization_adapter():
    request_repository = Mock(
        spec=CateringRequestRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )

    service = CateringRequestEventCoordinationService(
        request_repository=request_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create_event_from_request(
            17,
            subject=Mock(),
        )

    request_repository.get_by_id.assert_not_called()
    event_repository.add.assert_not_called()


def test_create_event_authorizes_before_loading_request():
    request_repository = Mock(
        spec=CateringRequestRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    service = CateringRequestEventCoordinationService(
        request_repository=request_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.create_event_from_request(
            17,
            subject=Mock(),
        )

    request_repository.get_by_id.assert_not_called()
    event_repository.add.assert_not_called()


def test_create_event_raises_when_request_does_not_exist():
    request_repository = Mock(
        spec=CateringRequestRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    request_repository.get_by_id.return_value = None

    subject = Mock()

    service = CateringRequestEventCoordinationService(
        request_repository=request_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityNotFoundException,
        match="Catering Request with id 999 was not found.",
    ):
        service.create_event_from_request(
            999,
            subject=subject,
        )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        CATERING_EVENT_CREATE.name,
    )
    request_repository.get_by_id.assert_called_once_with(999)
    event_repository.add.assert_not_called()


def test_create_event_maps_request_to_event():
    request_repository = Mock(
        spec=CateringRequestRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    request = _build_request()
    request_repository.get_by_id.return_value = request

    created_event = Mock(
        spec=CateringEvent,
    )
    event_repository.add.return_value = created_event

    subject = Mock()

    service = CateringRequestEventCoordinationService(
        request_repository=request_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.create_event_from_request(
        request.id,
        subject=subject,
    )

    assert result is created_event

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        CATERING_EVENT_CREATE.name,
    )
    request_repository.get_by_id.assert_called_once_with(
        request.id,
    )

    event_repository.add.assert_called_once()
    created_argument = event_repository.add.call_args.args[0]

    assert isinstance(created_argument, CateringEvent)
    assert created_argument.request_id == request.id
    assert created_argument.customer_id == request.customer_id
    assert created_argument.event_date == request.service_date
    assert created_argument.service_details == request.requested_service
    assert created_argument.attendance == request.attendance
    assert created_argument.operational_notes == request.notes
    assert created_argument.status == "REQUESTED"


def test_create_event_uses_requirements_when_request_has_no_notes():
    request_repository = Mock(
        spec=CateringRequestRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    request = _build_request()
    request.notes = None
    request_repository.get_by_id.return_value = request

    created_event = Mock(
        spec=CateringEvent,
    )
    event_repository.add.return_value = created_event

    service = CateringRequestEventCoordinationService(
        request_repository=request_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    service.create_event_from_request(
        request.id,
        subject=Mock(),
    )

    created_argument = event_repository.add.call_args.args[0]

    assert created_argument.operational_notes == request.requirements


def test_create_event_does_not_modify_request():
    request_repository = Mock(
        spec=CateringRequestRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    request = _build_request()
    request_repository.get_by_id.return_value = request

    event_repository.add.return_value = Mock(
        spec=CateringEvent,
    )

    original_values = {
        "status": request.status,
        "request_date": request.request_date,
        "service_date": request.service_date,
        "attendance": request.attendance,
    }

    service = CateringRequestEventCoordinationService(
        request_repository=request_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    service.create_event_from_request(
        request.id,
        subject=Mock(),
    )

    assert request.status == original_values["status"]
    assert request.request_date == original_values["request_date"]
    assert request.service_date == original_values["service_date"]
    assert request.attendance == original_values["attendance"]

    request_repository.update.assert_not_called()
