from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.procurement.models import (
    PurchaseRequest,
)

from app.modules.procurement.services import (
    PurchaseRequestService,
)

from app.modules.procurement.workflows import (
    PurchaseRequestWorkflow,
)


def _purchase_request(
    status: str,
    request_id: int = 1,
):
    return Mock(
        spec=PurchaseRequest,
        id=request_id,
        status=status,
    )


def test_submit_invokes_workflow_transition():
    repository = Mock()
    workflow = Mock(
        spec=PurchaseRequestWorkflow
    )

    workflow.transition.return_value = (
        SimpleNamespace(
            name=PurchaseRequestWorkflow.SUBMITTED
        )
    )

    purchase_request = _purchase_request(
        PurchaseRequestWorkflow.DRAFT
    )

    repository.update.return_value = (
        purchase_request
    )

    service = PurchaseRequestService(
        repository=repository,
        workflow=workflow,
    )

    result = service.submit(
        purchase_request
    )

    workflow.transition.assert_called_once_with(
        PurchaseRequestWorkflow.DRAFT,
        PurchaseRequestWorkflow.SUBMITTED,
    )

    assert (
        purchase_request.status
        == PurchaseRequestWorkflow.SUBMITTED
    )

    repository.update.assert_called_once_with(
        purchase_request
    )

    assert result is purchase_request


def test_approve_invokes_workflow_transition():
    repository = Mock()
    workflow = Mock(
        spec=PurchaseRequestWorkflow
    )

    workflow.transition.return_value = (
        SimpleNamespace(
            name=PurchaseRequestWorkflow.APPROVED
        )
    )

    purchase_request = _purchase_request(
        PurchaseRequestWorkflow.SUBMITTED
    )

    repository.update.return_value = (
        purchase_request
    )

    service = PurchaseRequestService(
        repository=repository,
        workflow=workflow,
    )

    result = service.approve(
        purchase_request
    )

    workflow.transition.assert_called_once_with(
        PurchaseRequestWorkflow.SUBMITTED,
        PurchaseRequestWorkflow.APPROVED,
    )

    assert (
        purchase_request.status
        == PurchaseRequestWorkflow.APPROVED
    )

    repository.update.assert_called_once_with(
        purchase_request
    )

    assert result is purchase_request


def test_submit_invalid_workflow_transition_prevents_update():
    repository = Mock()
    workflow = Mock(
        spec=PurchaseRequestWorkflow
    )

    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition."
    )

    purchase_request = _purchase_request(
        PurchaseRequestWorkflow.SUBMITTED
    )

    service = PurchaseRequestService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        service.submit(
            purchase_request
        )

    workflow.transition.assert_called_once_with(
        PurchaseRequestWorkflow.SUBMITTED,
        PurchaseRequestWorkflow.SUBMITTED,
    )

    repository.update.assert_not_called()

    assert (
        purchase_request.status
        == PurchaseRequestWorkflow.SUBMITTED
    )


def test_approve_invalid_workflow_transition_prevents_update():
    repository = Mock()
    workflow = Mock(
        spec=PurchaseRequestWorkflow
    )

    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition."
    )

    purchase_request = _purchase_request(
        PurchaseRequestWorkflow.DRAFT
    )

    service = PurchaseRequestService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        service.approve(
            purchase_request
        )

    workflow.transition.assert_called_once_with(
        PurchaseRequestWorkflow.DRAFT,
        PurchaseRequestWorkflow.APPROVED,
    )

    repository.update.assert_not_called()

    assert (
        purchase_request.status
        == PurchaseRequestWorkflow.DRAFT
    )
