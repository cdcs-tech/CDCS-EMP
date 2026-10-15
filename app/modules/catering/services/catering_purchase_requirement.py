"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Purchase Requirement application service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud import CRUDService
from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import (
    CateringEvent,
    CateringPurchaseRequirement,
    EventRequirement,
)
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringPurchaseRequirementRepository,
    EventRequirementRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import (
    CateringEventWorkflow,
)


class CateringPurchaseRequirementService(
    CRUDService[CateringPurchaseRequirement],
):
    """Create Catering-owned requirements for Procurement fulfilment."""

    CREATE_PERMISSION = (
        "CATERING.CATERING_PURCHASE_REQUIREMENT.CREATE"
    )

    def __init__(
        self,
        repository: (
            CateringPurchaseRequirementRepository | None
        ) = None,
        event_requirement_repository: (
            EventRequirementRepository | None
        ) = None,
        event_repository: (
            CateringEventRepository | None
        ) = None,
        authorization_adapter: (
            CateringAuthorizationAdapter | None
        ) = None,
    ) -> None:
        super().__init__(
            repository or CateringPurchaseRequirementRepository(),
            entity_name="CateringPurchaseRequirement",
        )
        self.event_requirement_repository = (
            event_requirement_repository
            or EventRequirementRepository()
        )
        self.event_repository = (
            event_repository
            or CateringEventRepository()
        )
        self.authorization_adapter = authorization_adapter

    def _authorize(self, subject: Any) -> None:
        """Authorize creation, failing closed without an adapter."""
        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for Catering Purchase Requirement creation."
            )

        self.authorization_adapter.authorize(
            subject,
            self.CREATE_PERMISSION,
        )

    def _get_event_requirement(
        self,
        event_requirement_id: int,
    ) -> EventRequirement:
        event_requirement = (
            self.event_requirement_repository.get_by_id(
                event_requirement_id
            )
        )
        if event_requirement is None:
            raise EntityNotFoundException(
                "EventRequirement",
                event_requirement_id,
            )
        return event_requirement

    def _get_confirmed_event(
        self,
        event_id: int,
    ) -> CateringEvent:
        event = self.event_repository.get_by_id(event_id)
        if event is None:
            raise EntityNotFoundException(
                "CateringEvent",
                event_id,
            )

        if event.status != CateringEventWorkflow.CONFIRMED:
            raise ValueError(
                "Catering Purchase Requirements may only be "
                "created for a CONFIRMED Catering Event."
            )

        return event

    def create(
        self,
        entity: CateringPurchaseRequirement,
        *,
        subject: Any,
    ) -> CateringPurchaseRequirement:
        """
        Create a DRAFT Catering Purchase Requirement.

        Only PROCUREMENT Event Requirements belonging to a
        CONFIRMED Catering Event are eligible. Procurement handoff
        remains a separate operation.
        """
        self._authorize(subject)

        event_requirement = self._get_event_requirement(
            entity.event_requirement_id
        )

        if event_requirement.fulfilment_type != "PROCUREMENT":
            raise ValueError(
                "Catering Purchase Requirements can only be "
                "created for PROCUREMENT Event Requirements."
            )

        self._get_confirmed_event(event_requirement.event_id)

        if event_requirement.purchase_requirement is not None:
            raise ValueError(
                "A Catering Purchase Requirement already exists "
                "for this Event Requirement."
            )

        # Lifecycle and handoff fields are service-controlled.
        entity.status = "DRAFT"
        entity.procurement_reference = None

        return super().create(entity)


__all__ = [
    "CateringPurchaseRequirementService",
]
