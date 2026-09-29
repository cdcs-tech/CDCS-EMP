from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityValidationException
from app.modules.catering.models import CateringEvent, CateringQuotation
from app.modules.catering.services import (
    CateringQuotationEventCoordinationService,
)
from app.modules.catering.workflows import CateringEventWorkflow


SUBJECT = object()


def _make_quotation(
    *,
    status: str = CateringEventWorkflow.REQUESTED,
    quotation_id: int = 101,
    event_id: int = 202,
    customer_id: int = 303,
) -> CateringQuotation:
    quotation = CateringQuotation(
        id=quotation_id,
        event_id=event_id,
        customer_id=customer_id,
        status=status,
    )
    return quotation


def _make_event(
    *,
    status: str = CateringEventWorkflow.REQUESTED,
    event_id: int = 202,
    customer_id: int = 303,
) -> CateringEvent:
    event = CateringEvent(
        id=event_id,
        request_id=404,
        customer_id=customer_id,
        status=status,
    )
    return event


def _make_service(
    *,
    quotation_repository: Mock | None = None,
    event_repository: Mock | None = None,
    authorization_adapter: Mock | None = None,
    event_workflow: Mock | None = None,
) -> tuple[CateringQuotationEventCoordinationService, Mock, Mock, Mock, Mock]:
    quotation_repository = quotation_repository or Mock()
    event_repository = event_repository or Mock()
    authorization_adapter = authorization_adapter or Mock()
    event_workflow = event_workflow or Mock()

    service = CateringQuotationEventCoordinationService(
        quotation_repository=quotation_repository,
        event_repository=event_repository,
        authorization_adapter=authorization_adapter,
        event_workflow=event_workflow,
    )

    return (
        service,
        quotation_repository,
        event_repository,
        authorization_adapter,
        event_workflow,
    )


def test_constructor_accepts_injected_dependencies() -> None:
    (
        service,
        quotation_repository,
        event_repository,
        authorization_adapter,
        event_workflow,
    ) = _make_service()

    assert service.quotation_repository is quotation_repository
    assert service.event_repository is event_repository
    assert service.authorization_adapter is authorization_adapter
    assert service.event_workflow is event_workflow


def test_missing_authorization_adapter_fails_closed() -> None:
    quotation_repository = Mock()
    event_repository = Mock()

    service = CateringQuotationEventCoordinationService(
        quotation_repository=quotation_repository,
        event_repository=event_repository,
        authorization_adapter=None,
        event_workflow=Mock(),
    )

    with pytest.raises(RuntimeError, match="authorization adapter is required"):
        service.progress_event_from_accepted_quotation(
            101,
            subject=SUBJECT,
        )

    quotation_repository.get_by_id.assert_not_called()
    event_repository.get_by_id.assert_not_called()


def test_successfully_progresses_event_from_accepted_quotation() -> None:
    quotation = _make_quotation(status=CateringEventWorkflow.REQUESTED)
    quotation.status = "ACCEPTED"
    event = _make_event()

    workflow_state = Mock()
    workflow_state.name = CateringEventWorkflow.QUOTED

    (
        service,
        quotation_repository,
        event_repository,
        authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = event
    event_workflow.transition.return_value = workflow_state
    event_repository.update.return_value = event

    result = service.progress_event_from_accepted_quotation(
        quotation.id,
        subject=SUBJECT,
    )

    authorization_adapter.authorize.assert_called_once_with(
        SUBJECT,
        "CATERING.CATERING_EVENT.QUOTE",
    )
    quotation_repository.get_by_id.assert_called_once_with(quotation.id)
    event_repository.get_by_id.assert_called_once_with(quotation.event_id)
    event_workflow.transition.assert_called_once_with(
        CateringEventWorkflow.REQUESTED,
        CateringEventWorkflow.QUOTED,
    )
    event_repository.update.assert_called_once_with(event)

    assert result is event
    assert event.status == CateringEventWorkflow.QUOTED
    assert quotation.status == "ACCEPTED"


def test_quotation_is_not_updated_during_coordination() -> None:
    quotation = _make_quotation()
    quotation.status = "ACCEPTED"
    event = _make_event()

    workflow_state = Mock()
    workflow_state.name = CateringEventWorkflow.QUOTED

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = event
    event_workflow.transition.return_value = workflow_state

    service.progress_event_from_accepted_quotation(
        quotation.id,
        subject=SUBJECT,
    )

    quotation_repository.update.assert_not_called()
    assert quotation.status == "ACCEPTED"


def test_quotation_not_found_rejected_without_event_access() -> None:
    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        _event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityValidationException,
        match="Quotation does not exist",
    ):
        service.progress_event_from_accepted_quotation(
            101,
            subject=SUBJECT,
        )

    event_repository.get_by_id.assert_not_called()
    event_repository.update.assert_not_called()


def test_event_not_found_rejected() -> None:
    quotation = _make_quotation()
    quotation.status = "ACCEPTED"

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityValidationException,
        match="Quotation event does not exist",
    ):
        service.progress_event_from_accepted_quotation(
            quotation.id,
            subject=SUBJECT,
        )

    event_workflow.transition.assert_not_called()
    event_repository.update.assert_not_called()


@pytest.mark.parametrize(
    "quotation_status",
    [
        "DRAFT",
        "ISSUED",
        "DECLINED",
        "EXPIRED",
    ],
)
def test_non_accepted_quotation_rejected(
    quotation_status: str,
) -> None:
    quotation = _make_quotation(status=quotation_status)

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation

    with pytest.raises(
        EntityValidationException,
        match="Only ACCEPTED quotations",
    ):
        service.progress_event_from_accepted_quotation(
            quotation.id,
            subject=SUBJECT,
        )

    event_repository.get_by_id.assert_not_called()
    event_workflow.transition.assert_not_called()
    event_repository.update.assert_not_called()


def test_quotation_event_relationship_mismatch_rejected() -> None:
    quotation = _make_quotation()
    quotation.status = "ACCEPTED"

    event = _make_event(event_id=999)

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = event

    with pytest.raises(
        EntityValidationException,
        match="Quotation must reference the associated event",
    ):
        service.progress_event_from_accepted_quotation(
            quotation.id,
            subject=SUBJECT,
        )

    event_workflow.transition.assert_not_called()
    event_repository.update.assert_not_called()


def test_customer_mismatch_rejected() -> None:
    quotation = _make_quotation()
    quotation.status = "ACCEPTED"

    event = _make_event(customer_id=999)

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = event

    with pytest.raises(
        EntityValidationException,
        match="Quotation customer must match",
    ):
        service.progress_event_from_accepted_quotation(
            quotation.id,
            subject=SUBJECT,
        )

    event_workflow.transition.assert_not_called()
    event_repository.update.assert_not_called()


@pytest.mark.parametrize(
    "event_status",
    [
        CateringEventWorkflow.QUOTED,
        CateringEventWorkflow.PENDING_CONFIRMATION,
        CateringEventWorkflow.CONFIRMED,
        CateringEventWorkflow.PLANNING,
        CateringEventWorkflow.READY,
        CateringEventWorkflow.IN_PRODUCTION,
        CateringEventWorkflow.DELIVERED,
        CateringEventWorkflow.COMPLETED,
        CateringEventWorkflow.CANCELLED,
    ],
)
def test_non_requested_event_rejected(event_status: str) -> None:
    quotation = _make_quotation()
    quotation.status = "ACCEPTED"
    event = _make_event(status=event_status)

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = event

    with pytest.raises(
        EntityValidationException,
        match="Only REQUESTED events",
    ):
        service.progress_event_from_accepted_quotation(
            quotation.id,
            subject=SUBJECT,
        )

    event_workflow.transition.assert_not_called()
    event_repository.update.assert_not_called()


def test_denied_authorization_does_not_load_or_mutate_entities() -> None:
    authorization_adapter = Mock()
    authorization_adapter.authorize.side_effect = RuntimeError(
        "Not authorized."
    )

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service(
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(RuntimeError, match="Not authorized"):
        service.progress_event_from_accepted_quotation(
            101,
            subject=SUBJECT,
        )

    quotation_repository.get_by_id.assert_not_called()
    event_repository.get_by_id.assert_not_called()
    event_workflow.transition.assert_not_called()
    event_repository.update.assert_not_called()


def test_workflow_rejection_does_not_persist_event() -> None:
    quotation = _make_quotation()
    quotation.status = "ACCEPTED"
    event = _make_event()

    (
        service,
        quotation_repository,
        event_repository,
        _authorization_adapter,
        event_workflow,
    ) = _make_service()

    quotation_repository.get_by_id.return_value = quotation
    event_repository.get_by_id.return_value = event
    event_workflow.transition.side_effect = EntityValidationException(
        "Invalid Event transition."
    )

    with pytest.raises(
        EntityValidationException,
        match="Invalid Event transition",
    ):
        service.progress_event_from_accepted_quotation(
            quotation.id,
            subject=SUBJECT,
        )

    assert event.status == CateringEventWorkflow.REQUESTED
    event_repository.update.assert_not_called()
