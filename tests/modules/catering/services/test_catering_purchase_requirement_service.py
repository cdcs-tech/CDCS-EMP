"""
Tests for the Catering Purchase Requirement application service.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import (
    CateringEvent,
    CateringPurchaseRequirement,
    EventRequirement,
)
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringPurchaseRequirementRepository,
    EventRequirementRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services.catering_purchase_requirement import (
    CateringPurchaseRequirementService,
)
from app.modules.catering.workflows import CateringEventWorkflow


def _event(status=CateringEventWorkflow.CONFIRMED):
    event = Mock(spec=CateringEvent)
    event.status = status
    return event


def _event_requirement(
    fulfilment_type="PROCUREMENT",
    event_id=7,
    purchase_requirement=None,
):
    requirement = Mock(spec=EventRequirement)
    requirement.id = 31
    requirement.event_id = event_id
    requirement.fulfilment_type = fulfilment_type
    requirement.purchase_requirement = purchase_requirement
    return requirement


def _purchase_requirement():
    requirement = Mock(spec=CateringPurchaseRequirement)
    requirement.event_requirement_id = 31
    requirement.status = "SUBMITTED"
    requirement.procurement_reference = "EXISTING-REFERENCE"
    return requirement


def _service(
    repository=None,
    event_requirement_repository=None,
    event_repository=None,
    authorization_adapter=None,
):
    return CateringPurchaseRequirementService(
        repository=repository or Mock(
            spec=CateringPurchaseRequirementRepository,
        ),
        event_requirement_repository=(
            event_requirement_repository
            or Mock(spec=EventRequirementRepository)
        ),
        event_repository=event_repository or Mock(
            spec=CateringEventRepository,
        ),
        authorization_adapter=(
            authorization_adapter
            or Mock(spec=CateringAuthorizationAdapter)
        ),
    )


def test_create_requires_authorization_adapter():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)

    service = CateringPurchaseRequirementService(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    event_requirement_repository.get_by_id.assert_not_called()
    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_authorizes_and_creates_draft_for_confirmed_event():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event_requirement_repository.get_by_id.return_value = (
        _event_requirement()
    )
    event_repository.get_by_id.return_value = _event()
    purchase_requirement = _purchase_requirement()
    repository.add.return_value = purchase_requirement

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )
    subject = Mock()

    result = service.create(
        purchase_requirement,
        subject=subject,
    )

    assert result is purchase_requirement
    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_PURCHASE_REQUIREMENT.CREATE",
    )
    event_requirement_repository.get_by_id.assert_called_once_with(31)
    event_repository.get_by_id.assert_called_once_with(7)
    assert purchase_requirement.status == "DRAFT"
    assert purchase_requirement.procurement_reference is None
    repository.add.assert_called_once_with(purchase_requirement)


def test_create_denied_does_not_validate_or_write():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(PermissionError, match="Denied"):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    event_requirement_repository.get_by_id.assert_not_called()
    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_rejects_missing_event_requirement():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    event_requirement_repository.get_by_id.return_value = None

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(EntityNotFoundException):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_rejects_inventory_fulfilment():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    event_requirement_repository.get_by_id.return_value = (
        _event_requirement(fulfilment_type="INVENTORY")
    )

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        ValueError,
        match="PROCUREMENT Event Requirements",
    ):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_rejects_missing_parent_event():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    event_requirement_repository.get_by_id.return_value = (
        _event_requirement()
    )
    event_repository.get_by_id.return_value = None

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(EntityNotFoundException):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_unconfirmed_event():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    event_requirement_repository.get_by_id.return_value = (
        _event_requirement()
    )
    event_repository.get_by_id.return_value = _event(
        status=CateringEventWorkflow.PLANNING,
    )

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        ValueError,
        match="CONFIRMED Catering Event",
    ):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_duplicate_purchase_requirement():
    repository = Mock(spec=CateringPurchaseRequirementRepository)
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(spec=CateringEventRepository)
    event_requirement_repository.get_by_id.return_value = (
        _event_requirement(
            purchase_requirement=Mock(
                spec=CateringPurchaseRequirement,
            ),
        )
    )
    event_repository.get_by_id.return_value = _event()

    service = _service(
        repository=repository,
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        service.create(
            _purchase_requirement(),
            subject=Mock(),
        )

    repository.add.assert_not_called()
