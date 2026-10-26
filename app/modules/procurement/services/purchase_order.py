"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order service.
"""

from __future__ import annotations

from sqlalchemy import select

from app.core.crud.service import CRUDService
from app.core.data import (
    PaginatedResult,
    QueryOptions,
)
from app.core.workflow.base import WorkflowState
from app.extensions import db
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

    Generic commercial edits and deletion are permitted only
    while the persisted Purchase Order remains in DRAFT.

    Workflow lifecycle transitions are handled separately and
    continue to be validated by PurchaseOrderWorkflow.
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

    def _get_persisted_status(
        self,
        purchase_order_id: int,
    ) -> str | None:
        """
        Read the persisted lifecycle state without relying on
        a potentially modified, session-tracked entity.
        """

        statement = select(
            PurchaseOrder.status
        ).where(
            PurchaseOrder.id == purchase_order_id
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def _require_draft(
        self,
        purchase_order_id: int,
        operation: str,
    ) -> None:
        """Reject commercial mutations unless the persisted PO is DRAFT."""

        persisted_status = self._get_persisted_status(
            purchase_order_id
        )

        if persisted_status is None:
            raise ValueError(
                "Purchase Order does not exist."
            )

        if persisted_status != PurchaseOrderWorkflow.DRAFT:
            raise ValueError(
                f"Cannot {operation} a Purchase Order "
                f"unless its persisted status is DRAFT."
            )

    def create(
        self,
        entity: PurchaseOrder,
    ) -> PurchaseOrder:
        """Create a Purchase Order only with a supported currency."""

        supported_currencies = {"USD", "SSP"}
        currency = entity.currency

        if currency not in supported_currencies:
            raise ValueError(
                "Purchase Order currency must be USD or SSP."
            )

        return super().create(entity)

    def update(
        self,
        entity: PurchaseOrder,
    ) -> PurchaseOrder:
        """
        Update commercial fields only while the persisted PO
        is in DRAFT. Workflow transitions use their own path.
        """

        persisted_status = self._get_persisted_status(
            entity.id
        )

        if persisted_status is None:
            raise ValueError(
                "Purchase Order does not exist."
            )

        if persisted_status != PurchaseOrderWorkflow.DRAFT:
            raise ValueError(
                "Cannot update a Purchase Order unless "
                "its persisted status is DRAFT."
            )

        if entity.status != persisted_status:
            raise ValueError(
                "Purchase Order status must be changed "
                "through its workflow actions."
            )

        return self.repository.update(
            entity
        )

    def delete(
        self,
        entity_id,
    ) -> None:
        """Delete a Purchase Order only while it is persistently DRAFT."""

        purchase_order = self.get(
            entity_id
        )

        self._require_draft(
            purchase_order.id,
            "delete",
        )

        self.repository.delete(
            purchase_order
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

    def _persist_workflow_transition(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        """
        Persist a validated lifecycle transition without
        routing it through the generic commercial-edit guard.
        """

        return self.repository.update(
            purchase_order
        )

    def submit(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.SUBMITTED,
        )
        return self._persist_workflow_transition(
            purchase_order
        )

    def approve(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.APPROVED,
        )
        return self._persist_workflow_transition(
            purchase_order
        )

    def reject(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.REJECTED,
        )
        return self._persist_workflow_transition(
            purchase_order
        )

    def return_to_draft(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.DRAFT,
        )
        return self._persist_workflow_transition(
            purchase_order
        )

    def cancel(
        self,
        purchase_order: PurchaseOrder,
    ) -> PurchaseOrder:
        self._transition_workflow(
            purchase_order,
            PurchaseOrderWorkflow.CANCELLED,
        )
        return self._persist_workflow_transition(
            purchase_order
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[PurchaseOrder]:
        return self.repository.paginate(options)


__all__ = [
    "PurchaseOrderService",
]
