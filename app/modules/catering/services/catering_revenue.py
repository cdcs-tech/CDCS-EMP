"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Revenue service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.crud import CRUDService
from app.core.crud.exceptions import EntityValidationException
from app.core.workflow.base import WorkflowState
from app.modules.catering.models import CateringRevenue
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringQuotationRepository,
    CateringRevenueRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import CateringRevenueWorkflow


class CateringRevenueService(CRUDService[CateringRevenue]):
    """
    Application service for Catering Revenue operations.

    Eligibility requires verified delivery context and an accepted
    quotation. Event status is supporting evidence, not an automatic
    eligibility or revenue-recognition trigger.

    Revenue recognition remains a separate explicit operation.
    """

    def __init__(
        self,
        repository: CateringRevenueRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: CateringRevenueWorkflow | None = None,
        event_repository: CateringEventRepository | None = None,
        quotation_repository: CateringQuotationRepository | None = None,
    ) -> None:
        super().__init__(
            repository or CateringRevenueRepository(),
            entity_name="CateringRevenue",
        )

        self.authorization_adapter = authorization_adapter
        self.workflow = workflow or CateringRevenueWorkflow()
        self.event_repository = (
            event_repository or CateringEventRepository()
        )
        self.quotation_repository = (
            quotation_repository or CateringQuotationRepository()
        )

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """Authorize a protected operation, failing closed by default."""

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Catering Revenue operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    @staticmethod
    def _required_text(
        value: str | None,
        field_label: str,
        *,
        max_length: int = 2000,
    ) -> str:
        """Validate and normalize a required text value."""

        if not isinstance(value, str) or not value.strip():
            raise EntityValidationException(
                f"{field_label} is required."
            )

        normalized = value.strip()

        if len(normalized) > max_length:
            raise EntityValidationException(
                f"{field_label} cannot exceed {max_length} characters."
            )

        return normalized

    @staticmethod
    def _validate_entity(
        revenue: CateringRevenue,
    ) -> None:
        """Validate the minimum Catering Revenue business facts."""

        if not isinstance(revenue.revenue_reference, str) or not (
            revenue.revenue_reference.strip()
        ):
            raise EntityValidationException(
                "Revenue reference is required."
            )

        if len(revenue.revenue_reference.strip()) > 100:
            raise EntityValidationException(
                "Revenue reference cannot exceed 100 characters."
            )

        if not isinstance(revenue.source_type, str) or not (
            revenue.source_type.strip()
        ):
            raise EntityValidationException(
                "Revenue source type is required."
            )

        if len(revenue.source_type.strip()) > 50:
            raise EntityValidationException(
                "Revenue source type cannot exceed 50 characters."
            )

        if not isinstance(revenue.source_reference, str) or not (
            revenue.source_reference.strip()
        ):
            raise EntityValidationException(
                "Revenue source reference is required."
            )

        if len(revenue.source_reference.strip()) > 100:
            raise EntityValidationException(
                "Revenue source reference cannot exceed 100 characters."
            )

        if revenue.amount is None:
            raise EntityValidationException(
                "Revenue amount is required."
            )

        if Decimal(str(revenue.amount)) < Decimal("0.00"):
            raise EntityValidationException(
                "Revenue amount cannot be negative."
            )

        if not isinstance(revenue.currency, str) or not (
            revenue.currency.strip()
        ):
            raise EntityValidationException(
                "Revenue currency is required."
            )

        if len(revenue.currency.strip()) != 3:
            raise EntityValidationException(
                "Revenue currency must be a three-letter code."
            )

        if revenue.revenue_date is None:
            raise EntityValidationException(
                "Revenue date is required."
            )

    def _transition_workflow(
        self,
        revenue: CateringRevenue,
        target_state: str,
    ) -> WorkflowState:
        """Validate and apply a Catering Revenue workflow transition."""

        state = self.workflow.transition(
            revenue.status,
            target_state,
        )

        revenue.status = state.name

        return state

    def _require_draft(
        self,
        revenue: CateringRevenue,
    ) -> None:
        if revenue.status != CateringRevenueWorkflow.DRAFT:
            raise EntityValidationException(
                "Only DRAFT Catering Revenue records can be modified "
                "or deleted."
            )

    def create(
        self,
        entity: CateringRevenue,
        *,
        subject: Any,
    ) -> CateringRevenue:
        """Create a new Catering Revenue record in DRAFT state."""

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.CREATE",
        )

        if entity.status != CateringRevenueWorkflow.DRAFT:
            raise EntityValidationException(
                "New Catering Revenue records must be created "
                "in DRAFT status."
            )

        self._validate_entity(entity)

        return super().create(entity)

    def update(
        self,
        entity: CateringRevenue,
        *,
        subject: Any,
    ) -> CateringRevenue:
        """Update a DRAFT Catering Revenue record."""

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.UPDATE",
        )

        persisted = self.get(entity.id)

        self._require_draft(persisted)

        if entity.status != CateringRevenueWorkflow.DRAFT:
            raise EntityValidationException(
                "Only DRAFT Catering Revenue records can be updated."
            )

        self._validate_entity(entity)

        return super().update(entity)

    def delete(
        self,
        entity_id: int,
        *,
        subject: Any,
    ) -> None:
        """Delete a DRAFT Catering Revenue record."""

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.DELETE",
        )

        revenue = self.get(entity_id)

        self._require_draft(revenue)

        self.repository.delete(revenue)

    def establish_eligibility(
        self,
        revenue: CateringRevenue,
        *,
        subject: Any,
        delivery_evidence: str,
        eligibility_reason: str,
        amount_adjustment_reason: str | None = None,
    ) -> CateringRevenue:
        """
        Establish eligibility against delivered services and an accepted
        quotation, without recognizing revenue.

        The eligibility quotation and timestamp are recorded only after
        all business validations and the workflow transition succeed.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.ESTABLISH_ELIGIBILITY",
        )

        self._require_draft(revenue)
        self._validate_entity(revenue)

        delivery_evidence = self._required_text(
            delivery_evidence,
            "Delivery evidence",
        )
        eligibility_reason = self._required_text(
            eligibility_reason,
            "Eligibility reason",
        )

        if revenue.event_id is None:
            raise EntityValidationException(
                "A Catering Event is required to establish revenue eligibility."
            )

        if revenue.customer_id is None:
            raise EntityValidationException(
                "A customer is required to establish revenue eligibility."
            )

        event = self.event_repository.get_by_id(revenue.event_id)

        if event is None:
            raise EntityValidationException(
                "The associated Catering Event could not be found."
            )

        if event.status not in {"DELIVERED", "COMPLETED"}:
            raise EntityValidationException(
                "Revenue eligibility requires an Event with DELIVERED "
                "or COMPLETED status."
            )

        if event.customer_id != revenue.customer_id:
            raise EntityValidationException(
                "Revenue customer must match the Catering Event customer."
            )

        quotation = self.quotation_repository.get_accepted_by_event_id(
            revenue.event_id
        )

        if quotation is None:
            raise EntityValidationException(
                "An accepted quotation is required to establish "
                "revenue eligibility."
            )

        if quotation.event_id != event.id:
            raise EntityValidationException(
                "The accepted quotation must belong to the associated "
                "Catering Event."
            )

        if quotation.customer_id != event.customer_id:
            raise EntityValidationException(
                "The accepted quotation customer must match the "
                "Catering Event customer."
            )

        if quotation.total_amount is None:
            raise EntityValidationException(
                "The accepted quotation must have a valid total amount."
            )

        adjustment_reason = None
        revenue_amount = Decimal(str(revenue.amount))
        quotation_amount = Decimal(str(quotation.total_amount))

        if revenue_amount != quotation_amount:
            adjustment_reason = self._required_text(
                amount_adjustment_reason,
                "Amount adjustment reason",
            )
        elif amount_adjustment_reason and amount_adjustment_reason.strip():
            adjustment_reason = self._required_text(
                amount_adjustment_reason,
                "Amount adjustment reason",
            )

        # Complete all validations before requesting the transition.
        self._transition_workflow(
            revenue,
            CateringRevenueWorkflow.ELIGIBLE,
        )

        revenue.eligibility_quotation_id = quotation.id
        revenue.delivery_evidence = delivery_evidence
        revenue.eligibility_reason = eligibility_reason
        revenue.amount_adjustment_reason = adjustment_reason
        revenue.eligible_at = datetime.now(timezone.utc)

        return super().update(revenue)

    def recognize(
        self,
        revenue: CateringRevenue,
        *,
        subject: Any,
    ) -> CateringRevenue:
        """
        Explicitly recognize eligible revenue.

        Recognition does not create a Finance record and is never
        inferred from Event status or quotation acceptance.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.RECOGNIZE",
        )

        self._transition_workflow(
            revenue,
            CateringRevenueWorkflow.RECOGNIZED,
        )

        revenue.recognized_at = datetime.now(timezone.utc)

        return super().update(revenue)

    def cancel(
        self,
        revenue: CateringRevenue,
        *,
        subject: Any,
    ) -> CateringRevenue:
        """Explicitly cancel DRAFT or ELIGIBLE Catering Revenue."""

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.CANCEL",
        )

        self._transition_workflow(
            revenue,
            CateringRevenueWorkflow.CANCELLED,
        )

        return super().update(revenue)


__all__ = [
    "CateringRevenueService",
]
