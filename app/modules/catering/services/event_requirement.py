"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event Requirement service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud import CRUDService
from app.core.crud.exceptions import EntityNotFoundException
from app.core.workflow.base import WorkflowState
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
from app.modules.catering.workflows import (
    CateringEventWorkflow,
    EventRequirementWorkflow,
)


class EventRequirementService(
    CRUDService[EventRequirement],
):
    """
    Application service for Catering Event Requirement operations.

    Event Requirement lifecycle transitions are delegated to
    EventRequirementWorkflow.

    Event association validation is performed at the Catering
    application-service boundary. Requirements may only be created
    or reassigned to confirmed Catering Events.

    Procurement, Inventory, Finance, Production, Delivery, and
    Catering Event lifecycle operations remain outside this service.

    Protected business operations are authorized through the
    Catering authorization adapter at the service boundary.
    """

    IDENTIFY_PERMISSION = (
        "CATERING.EVENT_REQUIREMENT.IDENTIFY"
    )
    READY_PERMISSION = (
        "CATERING.EVENT_REQUIREMENT.READY"
    )
    CANCEL_PERMISSION = (
        "CATERING.EVENT_REQUIREMENT.CANCEL"
    )

    def __init__(
        self,
        repository: EventRequirementRepository | None = None,
        event_repository: CateringEventRepository | None = None,
        authorization_adapter: (
            CateringAuthorizationAdapter | None
        ) = None,
        workflow: EventRequirementWorkflow | None = None,
        fulfilment_verifier: Any | None = None,
    ) -> None:
        super().__init__(
            repository or EventRequirementRepository(),
            entity_name="EventRequirement",
        )

        self.event_repository = (
            event_repository
            or CateringEventRepository()
        )
        self.authorization_adapter = (
            authorization_adapter
        )
        self.workflow = (
            workflow
            or EventRequirementWorkflow()
        )
        self.fulfilment_verifier = fulfilment_verifier

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Event Requirement operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Event Requirement operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def _get_confirmed_event(
        self,
        event_id: int,
    ) -> CateringEvent:
        """
        Retrieve and validate the associated Catering Event.

        Event Requirement planning is permitted only for a
        CONFIRMED Catering Event.
        """

        event = self.event_repository.get_by_id(
            event_id
        )

        if event is None:
            raise EntityNotFoundException(
                "CateringEvent",
                event_id,
            )

        if (
            event.status
            != CateringEventWorkflow.CONFIRMED
        ):
            raise ValueError(
                "Event Requirements may only be created "
                "or assigned to a CONFIRMED Catering Event."
            )

        return event

    def _transition_workflow(
        self,
        requirement: EventRequirement,
        target_state: str,
    ) -> WorkflowState:
        """
        Validate and apply an Event Requirement workflow transition.

        The workflow owns lifecycle transition validity. The service
        applies the resulting state to the entity; persistence remains
        the responsibility of the service operation.
        """

        state = self.workflow.transition(
            requirement.status,
            target_state,
        )

        requirement.status = state.name

        return state

    def create(
        self,
        entity: EventRequirement,
        *,
        subject: Any,
    ) -> EventRequirement:
        """
        Create an Event Requirement after authorization and
        confirmed-Event validation.
        """

        self._authorize(
            subject,
            "CATERING.EVENT_REQUIREMENT.CREATE",
        )

        self._get_confirmed_event(
            entity.event_id
        )

        return super().create(entity)

    def update(
        self,
        entity: EventRequirement,
        *,
        subject: Any,
    ) -> EventRequirement:
        """
        Update an Event Requirement after authorization and
        confirmed-Event validation.

        Revalidating the Event association prevents an ordinary
        update from moving a requirement to an unconfirmed Event.
        """

        self._authorize(
            subject,
            "CATERING.EVENT_REQUIREMENT.UPDATE",
        )

        self._get_confirmed_event(
            entity.event_id
        )

        return super().update(entity)

    def delete(
        self,
        entity_id: int,
        *,
        subject: Any,
    ) -> None:
        """
        Delete an Event Requirement after authorization.
        """

        self._authorize(
            subject,
            "CATERING.EVENT_REQUIREMENT.DELETE",
        )

        return super().delete(entity_id)

    def identify(
        self,
        requirement: EventRequirement,
        *,
        subject: Any,
    ) -> EventRequirement:
        """
        Identify an Event Requirement.

        IDENTIFY is a distinct lifecycle permission and therefore
        persists through the base CRUD update path rather than the
        authorization-protected UPDATE operation.
        """

        self._authorize(
            subject,
            self.IDENTIFY_PERMISSION,
        )

        self._transition_workflow(
            requirement,
            EventRequirementWorkflow.IDENTIFIED,
        )

        return super().update(requirement)

    def ready(
        self,
        requirement: EventRequirement,
        *,
        subject: Any,
    ) -> EventRequirement:
        """
        Mark an Event Requirement ready for its fulfilment path.

        READY represents Catering-side planning readiness only.
        It does not perform Inventory fulfilment or Procurement
        handoff.
        """

        self._authorize(
            subject,
            self.READY_PERMISSION,
        )

        self._transition_workflow(
            requirement,
            EventRequirementWorkflow.READY,
        )

        return super().update(requirement)

    def cancel(
        self,
        requirement: EventRequirement,
        *,
        subject: Any,
    ) -> EventRequirement:
        """
        Cancel an Event Requirement after authorization.

        CANCEL is a distinct lifecycle permission and therefore
        persists through the base CRUD update path rather than the
        authorization-protected UPDATE operation.
        """

        self._authorize(
            subject,
            self.CANCEL_PERMISSION,
        )

        self._transition_workflow(
            requirement,
            EventRequirementWorkflow.CANCELLED,
        )

        return super().update(requirement)


__all__ = [
    "EventRequirementService",
]
