"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order service.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.core.data import (
    PaginatedResult,
    QueryOptions,
)
from app.core.workflow.base import WorkflowState
from app.modules.procurement.models import PurchaseOrder
from app.modules.procurement.repositories import (
    PurchaseOrderRepository,
)
from app.modules.procurement.workflows import (
    PurchaseOrderWorkflow,
)


class PurchaseOrderService(
    CRUDService[PurchaseOrder],
):
    """
    Business service for Purchase Order entities.

    Workflow lifecycle enforcement is performed at the
    service boundary. The Purchase Order workflow owns
    lifecycle transition validity, while this service owns
    applying the resulting state to the entity and
    persisting the business change.
    """

    def __init__(
        self,
        repository: PurchaseOrderRepository | None = None,
        workflow: PurchaseOrderWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository or PurchaseOrderRepository(),
            entity_name="Purchase Order",
        )
        self.workflow = (
            workflow or PurchaseOrderWorkflow()
        )

    def _transition_workflow(
        self,
        purchase_order: PurchaseOrder,
        target_state: str,
    ) -> WorkflowState:
        state = self.workflow.transition(
            purchase_order.status,
            target_state,
        )
        purchase_order.status = state.name
        return state

    def submit(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.SUBMITTED,
        )
        return self.update(purchase_order)

    def approve(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.APPROVED,
        )
        return self.update(purchase_order)

    def reject(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.REJECTED,
        )
        return self.update(purchase_order)

    def return_to_draft(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.DRAFT,
        )
        return self.update(purchase_order)

    def cancel(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.CANCELLED,
        )
        return self.update(purchase_order)

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[PurchaseOrder]:
        return self.repository.paginate(options)


__all__ = [
    "PurchaseOrderService",
]
