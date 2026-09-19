"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order service workflow tests.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.procurement.models import PurchaseOrder
from app.modules.procurement.services import PurchaseOrderService
from app.modules.procurement.workflows import PurchaseOrderWorkflow


def _purchase_order(
    status: str,
) -> Mock:
    purchase_order = Mock(spec=PurchaseOrder)
    purchase_order.id = 1
    purchase_order.status = status
    return purchase_order


@pytest.mark.parametrize(
    ("method_name", "source", "target"),
    [
        (
            "submit",
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.SUBMITTED,
        ),
        (
            "approve",
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.APPROVED,
        ),
        (
            "reject",
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.REJECTED,
        ),
        (
            "return_to_draft",
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.DRAFT,
        ),
        (
            "cancel",
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.CANCELLED,
        ),
    ],
)
def test_purchase_order_service_applies_valid_workflow_transition(
    method_name,
    source,
    target,
):
    repository = Mock()
    workflow = Mock()
    purchase_order = _purchase_order(source)

    workflow.transition.return_value = SimpleNamespace(
        name=target,
    )
    repository.update.return_value = purchase_order

    service = PurchaseOrderService(
        repository=repository,
        workflow=workflow,
    )

    result = getattr(service, method_name)(
        purchase_order
    )

    workflow.transition.assert_called_once_with(
        source,
        target,
    )
    assert purchase_order.status == target
    repository.update.assert_called_once_with(
        purchase_order
    )
    assert result is purchase_order


@pytest.mark.parametrize(
    ("method_name", "source", "target"),
    [
        (
            "submit",
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.SUBMITTED,
        ),
        (
            "approve",
            PurchaseOrderWorkflow.DRAFT,
            PurchaseOrderWorkflow.APPROVED,
        ),
        (
            "reject",
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.REJECTED,
        ),
        (
            "return_to_draft",
            PurchaseOrderWorkflow.APPROVED,
            PurchaseOrderWorkflow.DRAFT,
        ),
        (
            "cancel",
            PurchaseOrderWorkflow.SUBMITTED,
            PurchaseOrderWorkflow.CANCELLED,
        ),
    ],
)
def test_purchase_order_service_rejects_invalid_workflow_transition(
    method_name,
    source,
    target,
):
    repository = Mock()
    workflow = Mock()
    purchase_order = _purchase_order(source)

    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition."
    )

    service = PurchaseOrderService(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        getattr(service, method_name)(
            purchase_order
        )

    workflow.transition.assert_called_once_with(
        source,
        target,
    )
    repository.update.assert_not_called()
    assert purchase_order.status == source
