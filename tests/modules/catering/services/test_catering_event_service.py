"""
Tests for the Catering Event application service.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import CateringEvent
from app.modules.catering.repositories import CateringEventRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import CateringEventService
from app.modules.catering.workflows import CateringEventWorkflow


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


def test_create_requires_authorization_adapter():
    """Verify protected creation fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    event = Mock(
        spec=CateringEvent,
    )

    service = CateringEventService(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create(
            event,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_authorizes_before_repository_write():
    """Verify creation uses the canonical Event CREATE permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event = Mock(
        spec=CateringEvent,
    )

    repository.add.return_value = event

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.create(
        event,
        subject=subject,
    )

    assert result is event

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CREATE",
    )

    repository.add.assert_called_once_with(
        event,
    )


def test_create_denied_does_not_write_to_repository():
    """Verify denied creation does not mutate the repository."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    event = Mock(
        spec=CateringEvent,
    )

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.create(
            event,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_update_requires_authorization_adapter():
    """Verify protected update fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    event = Mock(
        spec=CateringEvent,
    )

    service = CateringEventService(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.update(
            event,
            subject=Mock(),
        )

    repository.update.assert_not_called()


def test_update_authorizes_before_repository_write():
    """Verify update uses the canonical Event UPDATE permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event = Mock(
        spec=CateringEvent,
    )

    repository.update.return_value = event

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.update(
        event,
        subject=subject,
    )

    assert result is event

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.UPDATE",
    )

    repository.update.assert_called_once_with(
        event,
    )


def test_update_denied_does_not_write_to_repository():
    """Verify denied update does not mutate the repository."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    event = Mock(
        spec=CateringEvent,
    )

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.update(
            event,
            subject=Mock(),
        )

    repository.update.assert_not_called()


def test_delete_authorizes_before_repository_write():
    """Verify delete uses the canonical Event DELETE permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event = Mock(
        spec=CateringEvent,
    )

    repository.get_by_id.return_value = event

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    service.delete(
        1,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.DELETE",
    )

    repository.get_by_id.assert_called_once_with(
        1,
    )

    repository.delete.assert_called_once_with(
        event,
    )


def test_delete_requires_authorization_adapter():
    """Verify protected delete fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    service = CateringEventService(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.delete(
            1,
            subject=Mock(),
        )

    repository.get_by_id.assert_not_called()
    repository.delete.assert_not_called()


def test_delete_denied_does_not_write_to_repository():
    """Verify denied delete does not mutate the repository."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.delete(
            1,
            subject=Mock(),
        )

    repository.get_by_id.assert_not_called()
    repository.delete.assert_not_called()


def test_cancel_requires_authorization_adapter():
    """Verify protected cancellation fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.REQUESTED

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.cancel(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_cancel_authorizes_before_workflow_transition():
    """Verify cancellation uses the canonical Event CANCEL permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PENDING_CONFIRMATION

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.CANCELLED,
        },
    )()

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.cancel(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CANCEL",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PENDING_CONFIRMATION,
        CateringEventWorkflow.CANCELLED,
    )

    assert event.status == CateringEventWorkflow.CANCELLED

    repository.update.assert_called_once_with(
        event,
    )


def test_cancel_denied_does_not_transition_or_persist():
    """Verify denied cancellation does not change state or persist."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.REQUESTED

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.cancel(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.REQUESTED


def test_cancel_persists_without_requiring_update_permission():
    """
    Verify CANCEL persists through the base CRUD path rather than
    invoking the authorization-protected UPDATE method.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.REQUESTED

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.CANCELLED,
        },
    )()

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.cancel(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CANCEL",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.REQUESTED,
        CateringEventWorkflow.CANCELLED,
    )

    assert event.status == CateringEventWorkflow.CANCELLED

    repository.update.assert_called_once_with(
        event,
    )


def test_request_confirmation_requires_authorization_adapter():
    """Verify B4.4 confirmation-stage request fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.QUOTED

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.request_confirmation(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.QUOTED


def test_request_confirmation_authorizes_before_workflow_transition():
    """Verify B4.4 uses CONFIRM before progressing QUOTED events."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.PENDING_CONFIRMATION,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.QUOTED

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.request_confirmation(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CONFIRM",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.QUOTED,
        CateringEventWorkflow.PENDING_CONFIRMATION,
    )

    assert event.status == CateringEventWorkflow.PENDING_CONFIRMATION

    repository.update.assert_called_once_with(
        event,
    )


def test_request_confirmation_denied_does_not_transition_or_persist():
    """Verify denied B4.4 request does not change Event state."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.QUOTED

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.request_confirmation(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.QUOTED


def test_request_confirmation_persists_without_requiring_update_permission():
    """
    Verify B4.4 request-confirmation persistence uses the base CRUD path
    rather than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.PENDING_CONFIRMATION,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.QUOTED

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    subject = Mock()

    service.request_confirmation(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CONFIRM",
    )

    assert event.status == CateringEventWorkflow.PENDING_CONFIRMATION
    repository.update.assert_called_once_with(event)


def test_confirm_requires_authorization_adapter():
    """Verify B4.4 Event confirmation fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PENDING_CONFIRMATION

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.confirm(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.PENDING_CONFIRMATION


def test_confirm_authorizes_before_workflow_transition():
    """Verify B4.4 confirmation uses CONFIRM before progressing the Event."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.CONFIRMED,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PENDING_CONFIRMATION

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.confirm(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CONFIRM",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PENDING_CONFIRMATION,
        CateringEventWorkflow.CONFIRMED,
    )

    assert event.status == CateringEventWorkflow.CONFIRMED

    repository.update.assert_called_once_with(
        event,
    )


def test_confirm_denied_does_not_transition_or_persist():
    """Verify denied B4.4 confirmation does not change Event state."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PENDING_CONFIRMATION

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.confirm(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.PENDING_CONFIRMATION


def test_confirm_workflow_failure_does_not_persist_or_change_state():
    """Verify workflow rejection leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.side_effect = ValueError(
        "Invalid Event transition",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PENDING_CONFIRMATION

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event transition",
    ):
        service.confirm(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PENDING_CONFIRMATION,
        CateringEventWorkflow.CONFIRMED,
    )

    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.PENDING_CONFIRMATION


def test_confirm_persists_without_requiring_update_permission():
    """
    Verify B4.4 confirmation persistence uses the base CRUD path rather
    than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.CONFIRMED,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PENDING_CONFIRMATION

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.confirm(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.CONFIRM",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PENDING_CONFIRMATION,
        CateringEventWorkflow.CONFIRMED,
    )

    assert event.status == CateringEventWorkflow.CONFIRMED

    repository.update.assert_called_once_with(
        event,
    )


def test_plan_requires_authorization_adapter():
    """Verify Event planning fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.CONFIRMED

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.plan(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.CONFIRMED


def test_plan_authorizes_before_workflow_transition():
    """Verify Event planning uses the canonical PLAN permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.PLANNING,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.CONFIRMED

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.plan(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.PLAN",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.CONFIRMED,
        CateringEventWorkflow.PLANNING,
    )

    assert event.status == CateringEventWorkflow.PLANNING

    repository.update.assert_called_once_with(
        event,
    )


def test_plan_denied_does_not_transition_or_persist():
    """Verify denied Event planning leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.CONFIRMED

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.plan(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.CONFIRMED


def test_plan_workflow_failure_does_not_persist_or_change_state():
    """Verify workflow rejection leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.side_effect = ValueError(
        "Invalid Event transition",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.CONFIRMED

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event transition",
    ):
        service.plan(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.CONFIRMED,
        CateringEventWorkflow.PLANNING,
    )

    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.CONFIRMED


def test_plan_persists_without_requiring_update_permission():
    """
    Verify Event planning persists through the base CRUD path rather
    than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.PLANNING,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.CONFIRMED

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.plan(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.PLAN",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.CONFIRMED,
        CateringEventWorkflow.PLANNING,
    )

    assert event.status == CateringEventWorkflow.PLANNING

    repository.update.assert_called_once_with(
        event,
    )


def test_ready_requires_authorization_adapter():
    """Verify Event readiness fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PLANNING

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.ready(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.PLANNING


def test_ready_authorizes_before_workflow_transition():
    """Verify Event readiness uses the canonical READY permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.READY,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PLANNING

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.ready(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.READY",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PLANNING,
        CateringEventWorkflow.READY,
    )

    assert event.status == CateringEventWorkflow.READY

    repository.update.assert_called_once_with(
        event,
    )


def test_ready_denied_does_not_transition_or_persist():
    """Verify denied Event readiness leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PLANNING

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.ready(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.PLANNING


def test_ready_workflow_failure_does_not_persist_or_change_state():
    """Verify workflow rejection leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.side_effect = ValueError(
        "Invalid Event transition",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PLANNING

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event transition",
    ):
        service.ready(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PLANNING,
        CateringEventWorkflow.READY,
    )

    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.PLANNING


def test_ready_persists_without_requiring_update_permission():
    """
    Verify Event readiness persists through the base CRUD path rather
    than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.READY,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.PLANNING

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.ready(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.READY",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.PLANNING,
        CateringEventWorkflow.READY,
    )

    assert event.status == CateringEventWorkflow.READY

    repository.update.assert_called_once_with(
        event,
    )


def test_start_production_requires_authorization_adapter():
    """Verify production start fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.READY

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.start_production(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.READY


def test_start_production_authorizes_before_workflow_transition():
    """Verify production start uses the canonical permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.IN_PRODUCTION,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.READY

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.start_production(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.START_PRODUCTION",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.READY,
        CateringEventWorkflow.IN_PRODUCTION,
    )

    assert event.status == CateringEventWorkflow.IN_PRODUCTION

    repository.update.assert_called_once_with(
        event,
    )


def test_start_production_denied_does_not_transition_or_persist():
    """Verify denied production start leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.READY

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.start_production(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.READY


def test_start_production_workflow_failure_does_not_persist_or_change_state():
    """Verify workflow rejection leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.side_effect = ValueError(
        "Invalid Event transition",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.READY

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event transition",
    ):
        service.start_production(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.READY,
        CateringEventWorkflow.IN_PRODUCTION,
    )

    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.READY


def test_start_production_persists_without_requiring_update_permission():
    """
    Verify production start persists through the base CRUD path rather
    than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.IN_PRODUCTION,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.READY

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.start_production(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.START_PRODUCTION",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.READY,
        CateringEventWorkflow.IN_PRODUCTION,
    )

    assert event.status == CateringEventWorkflow.IN_PRODUCTION

    repository.update.assert_called_once_with(
        event,
    )


def test_deliver_requires_authorization_adapter():
    """Verify Event delivery fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.IN_PRODUCTION

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.deliver(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.IN_PRODUCTION


def test_deliver_authorizes_before_workflow_transition():
    """Verify Event delivery uses the canonical DELIVER permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.DELIVERED,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.IN_PRODUCTION

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.deliver(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.DELIVER",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.IN_PRODUCTION,
        CateringEventWorkflow.DELIVERED,
    )

    assert event.status == CateringEventWorkflow.DELIVERED

    repository.update.assert_called_once_with(
        event,
    )


def test_deliver_denied_does_not_transition_or_persist():
    """Verify denied Event delivery leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.IN_PRODUCTION

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.deliver(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.IN_PRODUCTION


def test_deliver_workflow_failure_does_not_persist_or_change_state():
    """Verify workflow rejection leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.side_effect = ValueError(
        "Invalid Event transition",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.IN_PRODUCTION

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event transition",
    ):
        service.deliver(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.IN_PRODUCTION,
        CateringEventWorkflow.DELIVERED,
    )

    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.IN_PRODUCTION


def test_deliver_persists_without_requiring_update_permission():
    """
    Verify Event delivery persists through the base CRUD path rather
    than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.DELIVERED,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.IN_PRODUCTION

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.deliver(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.DELIVER",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.IN_PRODUCTION,
        CateringEventWorkflow.DELIVERED,
    )

    assert event.status == CateringEventWorkflow.DELIVERED

    repository.update.assert_called_once_with(
        event,
    )



def test_start_production_blocks_when_readiness_check_fails():
    """Verify failed readiness prevents production transition and persistence."""

    repository = Mock(spec=CateringEventRepository)
    authorization_adapter = Mock(spec=CateringAuthorizationAdapter)
    workflow = Mock(spec=CateringEventWorkflow)
    readiness_service = Mock()

    event = Mock(spec=CateringEvent)
    event.status = CateringEventWorkflow.READY
    subject = Mock()

    readiness_service.ensure_production_ready.side_effect = RuntimeError(
        "Mandatory event requirements are not fulfilled."
    )

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
        readiness_service=readiness_service,
    )

    with pytest.raises(
        RuntimeError,
        match="Mandatory event requirements are not fulfilled",
    ):
        service.start_production(event, subject=subject)

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.START_PRODUCTION",
    )
    readiness_service.ensure_production_ready.assert_called_once_with(event)
    workflow.transition.assert_not_called()
    repository.update.assert_not_called()
    assert event.status == CateringEventWorkflow.READY



def test_complete_requires_authorization_adapter():
    """Verify Event completion fails closed without an adapter."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.DELIVERED

    service = CateringEventService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.complete(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.DELIVERED


def test_complete_authorizes_before_workflow_transition():
    """Verify Event completion uses the canonical COMPLETE permission."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.COMPLETED,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.DELIVERED

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.complete(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.COMPLETE",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.DELIVERED,
        CateringEventWorkflow.COMPLETED,
    )

    assert event.status == CateringEventWorkflow.COMPLETED

    repository.update.assert_called_once_with(
        event,
    )


def test_complete_denied_does_not_transition_or_persist():
    """Verify denied Event completion leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.DELIVERED

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.complete(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.DELIVERED


def test_complete_workflow_failure_does_not_persist_or_change_state():
    """Verify workflow rejection leaves the Event unchanged."""

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.side_effect = ValueError(
        "Invalid Event transition",
    )

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.DELIVERED

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid Event transition",
    ):
        service.complete(
            event,
            subject=Mock(),
        )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.DELIVERED,
        CateringEventWorkflow.COMPLETED,
    )

    repository.update.assert_not_called()

    assert event.status == CateringEventWorkflow.DELIVERED


def test_complete_persists_without_requiring_update_permission():
    """
    Verify Event completion persists through the base CRUD path rather
    than invoking the authorization-protected UPDATE operation.
    """

    repository = Mock(
        spec=CateringEventRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    workflow = Mock(
        spec=CateringEventWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringEventWorkflow.COMPLETED,
        },
    )()

    event = Mock(
        spec=CateringEvent,
    )

    event.status = CateringEventWorkflow.DELIVERED

    subject = Mock()

    service = CateringEventService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.complete(
        event,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_EVENT.COMPLETE",
    )

    workflow.transition.assert_called_once_with(
        CateringEventWorkflow.DELIVERED,
        CateringEventWorkflow.COMPLETED,
    )

    assert event.status == CateringEventWorkflow.COMPLETED

    repository.update.assert_called_once_with(
        event,
    )


def test_get_delegates_to_repository():
    repository = Mock(
        spec=CateringEventRepository
    )

    event = Mock(
        spec=CateringEvent,
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
