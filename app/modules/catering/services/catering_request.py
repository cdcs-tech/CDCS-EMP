"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Request service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud import CRUDService
from app.core.workflow.base import WorkflowState
from app.modules.catering.models import CateringRequest
from app.modules.catering.repositories import CateringRequestRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import CateringRequestWorkflow


class CateringRequestService(CRUDService[CateringRequest]):
    """
    Application service for Catering Request operations.

    Workflow lifecycle transitions and Request-to-Event coordination
    are intentionally separated. Request-to-Event coordination and
    quotation confirmation remain outside this service until their
    corresponding B3/B4 contracts are implemented.

    Protected business operations are authorized through the
    Catering authorization adapter at the service boundary.
    """

    def __init__(
        self,
        repository: CateringRequestRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: CateringRequestWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository or CateringRequestRepository(),
            entity_name="CateringRequest",
        )

        self.authorization_adapter = authorization_adapter
        self.workflow = workflow or CateringRequestWorkflow()

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering Request operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Catering Request operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def _transition_workflow(
        self,
        request: CateringRequest,
        target_state: str,
    ) -> WorkflowState:
        """
        Validate and apply a Catering Request workflow transition.

        The workflow owns lifecycle transition validity. The service
        applies the resulting state to the entity; persistence remains
        the responsibility of the service operation.
        """

        state = self.workflow.transition(
            request.status,
            target_state,
        )

        request.status = state.name

        return state

    def create(
        self,
        entity: CateringRequest,
        *,
        subject: Any,
    ) -> CateringRequest:
        """
        Create a Catering Request after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REQUEST.CREATE",
        )

        return super().create(entity)

    def update(
        self,
        entity: CateringRequest,
        *,
        subject: Any,
    ) -> CateringRequest:
        """
        Update a Catering Request after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REQUEST.UPDATE",
        )

        return super().update(entity)

    def delete(
        self,
        entity_id: int,
        *,
        subject: Any,
    ) -> None:
        """
        Delete a Catering Request after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REQUEST.DELETE",
        )

        return super().delete(entity_id)

    def submit(
        self,
        request: CateringRequest,
        *,
        subject: Any,
    ) -> CateringRequest:
        """
        Submit a Catering Request after authorization.

        SUBMIT is a distinct lifecycle permission and therefore
        persists through the base CRUD update path rather than the
        authorization-protected UPDATE operation.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REQUEST.SUBMIT",
        )

        self._transition_workflow(
            request,
            CateringRequestWorkflow.SUBMITTED,
        )

        return super().update(request)


__all__ = [
    "CateringRequestService",
]
