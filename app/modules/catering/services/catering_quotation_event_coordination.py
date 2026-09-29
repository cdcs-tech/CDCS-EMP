from __future__ import annotations

from typing import Any

from app.core.crud.exceptions import EntityValidationException
from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.core.workflow.base import WorkflowState
from app.modules.catering.models import CateringEvent, CateringQuotation
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringQuotationRepository,
)
from app.modules.catering.security.authorization import CateringAuthorizationAdapter
from app.modules.catering.workflows import CateringEventWorkflow


class CateringQuotationEventCoordinationService:
    """
    Application service for coordinating an accepted Catering Quotation
    with its associated Catering Event.

    B4.3 provides the explicit coordination boundary for progressing an
    associated Event from REQUESTED to QUOTED after quotation acceptance.

    Quotation lifecycle ownership remains with CateringQuotationService.
    Event lifecycle validity remains with CateringEventWorkflow.

    This service performs no downstream Procurement, Inventory, Finance,
    Expense, Production, Delivery, or Reporting side effects.
    """

    QUOTE_PERMISSION = "CATERING.CATERING_EVENT.QUOTE"

    def __init__(
        self,
        quotation_repository: CateringQuotationRepository | None = None,
        event_repository: CateringEventRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        event_workflow: CateringEventWorkflow | None = None,
    ) -> None:
        self.quotation_repository = (
            quotation_repository or CateringQuotationRepository()
        )
        self.event_repository = event_repository or CateringEventRepository()
        self.authorization_adapter = authorization_adapter
        self.event_workflow = event_workflow or CateringEventWorkflow()

    def _authorize(self, subject: Any) -> None:
        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for quotation/event coordination operations."
            )

        self.authorization_adapter.authorize(
            subject,
            self.QUOTE_PERMISSION,
        )

    def _load_quotation(self, quotation_id: int) -> CateringQuotation:
        quotation = self.quotation_repository.get_by_id(quotation_id)

        if quotation is None:
            raise EntityValidationException(
                "Quotation does not exist."
            )

        return quotation

    def _validate_quotation(
        self,
        quotation: CateringQuotation,
    ) -> None:
        if quotation.status != "ACCEPTED":
            raise EntityValidationException(
                "Only ACCEPTED quotations can progress an associated event."
            )

        if quotation.event_id is None:
            raise EntityValidationException(
                "Quotation must reference an event."
            )

        if quotation.customer_id is None:
            raise EntityValidationException(
                "Quotation must reference a customer."
            )

    def _load_event(self, quotation: CateringQuotation) -> CateringEvent:
        event = self.event_repository.get_by_id(quotation.event_id)

        if event is None:
            raise EntityValidationException(
                "Quotation event does not exist."
            )

        return event

    def _validate_relationship(
        self,
        quotation: CateringQuotation,
        event: CateringEvent,
    ) -> None:
        if quotation.event_id != event.id:
            raise EntityValidationException(
                "Quotation must reference the associated event."
            )

        if quotation.customer_id != event.customer_id:
            raise EntityValidationException(
                "Quotation customer must match the event customer."
            )

    def _validate_event_state(self, event: CateringEvent) -> None:
        if event.status != CateringEventWorkflow.REQUESTED:
            raise EntityValidationException(
                "Only REQUESTED events can be progressed from an accepted quotation."
            )

    def _transition_event(
        self,
        event: CateringEvent,
    ) -> WorkflowState:
        return self.event_workflow.transition(
            event.status,
            CateringEventWorkflow.QUOTED,
        )

    def progress_event_from_accepted_quotation(
        self,
        quotation_id: int,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Progress an associated Event from REQUESTED to QUOTED when its
        Catering Quotation has been accepted.

        Quotation status remains unchanged. Event lifecycle validity is
        delegated to CateringEventWorkflow.
        """
        self._authorize(subject)

        quotation = self._load_quotation(quotation_id)
        self._validate_quotation(quotation)

        event = self._load_event(quotation)
        self._validate_relationship(quotation, event)
        self._validate_event_state(event)

        state = self._transition_event(event)
        event.status = state.name

        return self.event_repository.update(event)


__all__ = ["CateringQuotationEventCoordinationService"]
