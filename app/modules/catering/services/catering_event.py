"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud import CRUDService
from app.core.workflow.base import WorkflowState
from app.modules.catering.models import CateringEvent
from app.modules.catering.repositories import CateringEventRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import CateringEventWorkflow


class CateringEventService(CRUDService[CateringEvent]):
    """
    Application service for Catering Event operations.

    Business lifecycle transitions are delegated to CateringEventWorkflow.
    Quotation/event coordination is handled by its dedicated Catering
    application-service boundary.

    Protected business operations are authorized through the
    Catering authorization adapter at the service boundary.
    """

    CONFIRM_PERMISSION = "CATERING.CATERING_EVENT.CONFIRM"
    PLAN_PERMISSION = "CATERING.CATERING_EVENT.PLAN"
    READY_PERMISSION = "CATERING.CATERING_EVENT.READY"
    START_PRODUCTION_PERMISSION = (
        "CATERING.CATERING_EVENT.START_PRODUCTION"
    )
    DELIVER_PERMISSION = "CATERING.CATERING_EVENT.DELIVER"
    COMPLETE_PERMISSION = "CATERING.CATERING_EVENT.COMPLETE"

    def __init__(
        self,
        repository: CateringEventRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: CateringEventWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository or CateringEventRepository(),
            entity_name="CateringEvent",
        )

        self.authorization_adapter = authorization_adapter
        self.workflow = workflow or CateringEventWorkflow()

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering Event operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Catering Event operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def _transition_workflow(
        self,
        event: CateringEvent,
        target_state: str,
    ) -> WorkflowState:
        """
        Validate and apply a Catering Event workflow transition.

        The workflow owns lifecycle transition validity. The service
        applies the resulting state to the entity; persistence remains
        the responsibility of the service operation.
        """

        state = self.workflow.transition(
            event.status,
            target_state,
        )

        event.status = state.name

        return state

    def create(
        self,
        entity: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Create a Catering Event after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_EVENT.CREATE",
        )

        return super().create(entity)

    def update(
        self,
        entity: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Update a Catering Event after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_EVENT.UPDATE",
        )

        return super().update(entity)

    def delete(
        self,
        entity_id: int,
        *,
        subject: Any,
    ) -> None:
        """
        Delete a Catering Event after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_EVENT.DELETE",
        )

        return super().delete(entity_id)

    def cancel(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Cancel a Catering Event after authorization.

        CANCEL is a distinct lifecycle permission and therefore
        persists through the base CRUD update path rather than the
        authorization-protected UPDATE operation.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_EVENT.CANCEL",
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.CANCELLED,
        )

        return super().update(event)

    def request_confirmation(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an Event from QUOTED to PENDING_CONFIRMATION.

        B4.4 treats this as a distinct, auditable confirmation-stage
        operation. Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.CONFIRM_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.PENDING_CONFIRMATION,
        )

        return super().update(event)

    def confirm(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Confirm an Event from PENDING_CONFIRMATION to CONFIRMED.

        Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.CONFIRM_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.CONFIRMED,
        )

        return super().update(event)

    def plan(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an Event from CONFIRMED to PLANNING.

        Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.PLAN_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.PLANNING,
        )

        return super().update(event)

    def ready(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an Event from PLANNING to READY.

        Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.READY_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.READY,
        )

        return super().update(event)

    def start_production(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an Event from READY to IN_PRODUCTION.

        Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.START_PRODUCTION_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.IN_PRODUCTION,
        )

        return super().update(event)

    def deliver(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an Event from IN_PRODUCTION to DELIVERED.

        Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.DELIVER_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.DELIVERED,
        )

        return super().update(event)

    def complete(
        self,
        event: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an Event from DELIVERED to COMPLETED.

        Event lifecycle validity remains delegated to
        CateringEventWorkflow.
        """

        self._authorize(
            subject,
            self.COMPLETE_PERMISSION,
        )

        self._transition_workflow(
            event,
            CateringEventWorkflow.COMPLETED,
        )

        return super().update(event)


__all__ = [
    "CateringEventService",
]
