"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Request service.
"""

from __future__ import annotations

from app.core.crud.service import (
    CRUDService,
)

from app.core.data import (
    PaginatedResult,
    QueryOptions,
)

from app.core.workflow.base import (
    WorkflowState,
)

from app.modules.procurement.models import (
    PurchaseRequest,
)

from app.modules.procurement.repositories import (
    PurchaseRequestRepository,
)

from app.modules.procurement.workflows import (
    PurchaseRequestWorkflow,
)


class PurchaseRequestService(
    CRUDService[PurchaseRequest],
):
    """
    Business service for Purchase Request entities.

    Workflow lifecycle enforcement is performed at the
    service boundary. The Purchase Request workflow owns
    lifecycle transition validity, while this service owns
    applying the resulting state to the entity and
    persisting the business change.
    """

    def __init__(
        self,
        repository: PurchaseRequestRepository | None = None,
        workflow: PurchaseRequestWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository
            or PurchaseRequestRepository(),
            entity_name="Purchase Request",
        )

        self.workflow = (
            workflow
            or PurchaseRequestWorkflow()
        )

    def _transition_workflow(
        self,
        purchase_request: PurchaseRequest,
        target_state: str,
    ) -> WorkflowState:
        """
        Validate and apply a Purchase Request workflow transition.

        The workflow remains authoritative for lifecycle validity.
        This service applies the resulting workflow state to the
        entity. Persistence remains the responsibility of the
        calling business operation.
        """

        state = self.workflow.transition(
            purchase_request.status,
            target_state,
        )

        purchase_request.status = state.name

        return state

    def submit(
        self,
        purchase_request: PurchaseRequest,
    ) -> PurchaseRequest:
        """
        Submit a Purchase Request through its workflow.
        """

        self._transition_workflow(
            purchase_request,
            PurchaseRequestWorkflow.SUBMITTED,
        )

        return self.update(
            purchase_request
        )

    def approve(
        self,
        purchase_request: PurchaseRequest,
    ) -> PurchaseRequest:
        """
        Approve a Purchase Request through its workflow.
        """

        self._transition_workflow(
            purchase_request,
            PurchaseRequestWorkflow.APPROVED,
        )

        return self.update(
            purchase_request
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[PurchaseRequest]:
        """
        Return a paginated Purchase Request result.
        """

        return self.repository.paginate(
            options
        )


__all__ = [
    "PurchaseRequestService",
]
