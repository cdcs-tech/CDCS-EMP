"""
Tests for the Catering Event Requirement application service.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import (
    CateringEvent,
    EventRequirement,
)
from app.modules.catering.repositories import (
    CateringEventRepository,
    EventRequirementRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import EventRequirementService
from app.modules.catering.workflows import (
    CateringEventWorkflow,
    EventRequirementWorkflow,
)


def _confirmed_event():
    event = Mock(spec=CateringEvent)
    event.status = CateringEventWorkflow.CONFIRMED
    return event


def _requirement(
    status=EventRequirementWorkflow.DRAFT,
    event_id=1,
):
    requirement = Mock(spec=EventRequirement)
    requirement.event_id = event_id
    requirement.status = status
    return requirement


def _service(
    repository=None,
    event_repository=None,
    authorization_adapter=None,
    workflow=None,
):
    return EventRequirementService(
        repository=repository
        or Mock(spec=EventRequirementRepository),
        event_repository=event_repository
        or Mock(spec=CateringEventRepository),
        authorization_adapter=authorization_adapter
        or Mock(spec=CateringAuthorizationAdapter),
        workflow=workflow
        or Mock(spec=EventRequirementWorkflow),
    )


def test_service_uses_default_repository():
    service = EventRequirementService()

    assert isinstance(
        service.repository,
        EventRequirementRepository,
    )


def test_service_accepts_injected_repository():
    repository = Mock(
        spec=EventRequirementRepository,
    )

    service = EventRequirementService(
        repository=repository,
    )

    assert service.repository is repository


def test_create_requires_authorization_adapter():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    requirement = _requirement()

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create(
            requirement,
            subject=Mock(),
        )

    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_authorizes_before_event_validation_and_write():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    requirement = _requirement()
    event_repository.get_by_id.return_value = _confirmed_event()
    repository.add.return_value = requirement

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    subject = Mock()

    result = service.create(
        requirement,
        subject=subject,
    )

    assert result is requirement

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EVENT_REQUIREMENT.CREATE",
    )
    event_repository.get_by_id.assert_called_once_with(
        1,
    )
    repository.add.assert_called_once_with(
        requirement,
    )


def test_create_denied_does_not_validate_or_write():
    repository = Mock(
        spec=EventRequirementRepository,
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

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.create(
            _requirement(),
            subject=Mock(),
        )

    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_rejects_missing_event():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event_repository.get_by_id.return_value = None

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityNotFoundException,
    ):
        service.create(
            _requirement(),
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_unconfirmed_event():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event = Mock(spec=CateringEvent)
    event.status = CateringEventWorkflow.PLANNING
    event_repository.get_by_id.return_value = event

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        ValueError,
        match="CONFIRMED Catering Event",
    ):
        service.create(
            _requirement(),
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_update_requires_authorization_adapter():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.update(
            _requirement(),
            subject=Mock(),
        )

    event_repository.get_by_id.assert_not_called()
    repository.update.assert_not_called()


def test_update_validates_confirmed_event_before_write():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    requirement = _requirement()
    event_repository.get_by_id.return_value = _confirmed_event()
    repository.update.return_value = requirement
    subject = Mock()

    service = EventRequirementService(
        repository=repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.update(
        requirement,
        subject=subject,
    )

    assert result is requirement
    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EVENT_REQUIREMENT.UPDATE",
    )
    event_repository.get_by_id.assert_called_once_with(1)
    repository.update.assert_called_once_with(requirement)


def test_delete_authorizes_before_repository_delete():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    requirement = _requirement()

    repository.get_by_id.return_value = requirement

    service = EventRequirementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    subject = Mock()

    service.delete(
        1,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EVENT_REQUIREMENT.DELETE",
    )
    repository.get_by_id.assert_called_once_with(1)
    repository.delete.assert_called_once_with(requirement)


def test_identify_authorizes_before_transition():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    workflow = Mock(
        spec=EventRequirementWorkflow,
    )

    requirement = _requirement()
    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": EventRequirementWorkflow.IDENTIFIED},
    )()

    service = EventRequirementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    subject = Mock()

    service.identify(
        requirement,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EVENT_REQUIREMENT.IDENTIFY",
    )
    workflow.transition.assert_called_once_with(
        EventRequirementWorkflow.DRAFT,
        EventRequirementWorkflow.IDENTIFIED,
    )
    assert (
        requirement.status
        == EventRequirementWorkflow.IDENTIFIED
    )
    repository.update.assert_called_once_with(
        requirement,
    )


def test_ready_authorizes_and_persists_without_fulfilment_verification():
    """Verify READY represents Catering-side planning readiness."""

    repository = Mock(spec=EventRequirementRepository)
    authorization_adapter = Mock(spec=CateringAuthorizationAdapter)
    workflow = Mock(spec=EventRequirementWorkflow)
    fulfilment_verifier = Mock()

    requirement = _requirement(
        status=EventRequirementWorkflow.IDENTIFIED,
    )
    subject = Mock()

    service = EventRequirementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
        fulfilment_verifier=fulfilment_verifier,
    )

    result = service.ready(
        requirement,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EVENT_REQUIREMENT.READY",
    )
    workflow.transition.assert_called_once()
    repository.update.assert_called_once_with(requirement)
    fulfilment_verifier.ensure_fulfilled.assert_not_called()
    assert result is repository.update.return_value


@pytest.mark.parametrize(
    "initial_status",
    [
        EventRequirementWorkflow.DRAFT,
        EventRequirementWorkflow.IDENTIFIED,
    ],
)
def test_cancel_authorizes_and_persists(
    initial_status,
):
    repository = Mock(
        spec=EventRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    workflow = Mock(
        spec=EventRequirementWorkflow,
    )

    requirement = _requirement(
        status=initial_status,
    )
    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": EventRequirementWorkflow.CANCELLED},
    )()

    service = EventRequirementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    subject = Mock()

    service.cancel(
        requirement,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EVENT_REQUIREMENT.CANCEL",
    )
    workflow.transition.assert_called_once_with(
        initial_status,
        EventRequirementWorkflow.CANCELLED,
    )
    assert (
        requirement.status
        == EventRequirementWorkflow.CANCELLED
    )
    repository.update.assert_called_once_with(
        requirement,
    )


def test_lifecycle_operation_does_not_require_update_permission():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    workflow = Mock(
        spec=EventRequirementWorkflow,
    )

    requirement = _requirement()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": EventRequirementWorkflow.IDENTIFIED},
    )()

    service = EventRequirementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.identify(
        requirement,
        subject=Mock(),
    )

    assert (
        authorization_adapter.authorize.call_args.args[1]
        == "CATERING.EVENT_REQUIREMENT.IDENTIFY"
    )
    repository.update.assert_called_once_with(
        requirement,
    )


def test_workflow_failure_does_not_persist_or_change_state():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    workflow = Mock(
        spec=EventRequirementWorkflow,
    )

    requirement = _requirement()
    workflow.transition.side_effect = ValueError(
        "Invalid Event Requirement transition",
    )

    service = EventRequirementService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event Requirement transition",
    ):
        service.identify(
            requirement,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        EventRequirementWorkflow.DRAFT,
        EventRequirementWorkflow.IDENTIFIED,
    )
    repository.update.assert_not_called()
    assert (
        requirement.status
        == EventRequirementWorkflow.DRAFT
    )


def test_get_uses_inherited_crud_behavior():
    repository = Mock(
        spec=EventRequirementRepository,
    )
    requirement = _requirement()

    repository.get_by_id.return_value = requirement

    service = EventRequirementService(
        repository=repository,
    )

    result = service.get(1)

    assert result is requirement
    repository.get_by_id.assert_called_once_with(1)
