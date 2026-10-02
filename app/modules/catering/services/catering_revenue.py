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
from app.modules.catering.repositories import CateringRevenueRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import CateringRevenueWorkflow


class CateringRevenueService(CRUDService[CateringRevenue]):
    """
    Application service for Catering Revenue operations.

    The service owns authorization, business validation, and
    lifecycle coordination.

    The workflow owns lifecycle transition validity.

    Revenue recognition is explicit and is never inferred from
    Catering Event status.
    """

    def __init__(
        self,
        repository: CateringRevenueRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: CateringRevenueWorkflow | None = None,
    ) -> None:
        super().__init__(
            repository or CateringRevenueRepository(),
            entity_name="CateringRevenue",
        )

        self.authorization_adapter = authorization_adapter
        self.workflow = workflow or CateringRevenueWorkflow()

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering Revenue operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

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
    def _validate_entity(
        revenue: CateringRevenue,
    ) -> None:
        """
        Validate the minimum Catering Revenue business facts.
        """

        if not revenue.revenue_reference.strip():
            raise EntityValidationException(
                "Revenue reference is required."
            )

        if not revenue.source_type.strip():
            raise EntityValidationException(
                "Revenue source type is required."
            )

        if not revenue.source_reference.strip():
            raise EntityValidationException(
                "Revenue source reference is required."
            )

        if revenue.amount is None:
            raise EntityValidationException(
                "Revenue amount is required."
            )

        if Decimal(str(revenue.amount)) < Decimal("0.00"):
            raise EntityValidationException(
                "Revenue amount cannot be negative."
            )

        if not revenue.currency or not revenue.currency.strip():
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
        """
        Validate and apply a Catering Revenue workflow transition.
        """

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
        """
        Create a new Catering Revenue record.

        New records must begin in DRAFT state.
        """

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
        """
        Update a DRAFT Catering Revenue record.
        """

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
        """
        Delete a DRAFT Catering Revenue record.
        """

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
    ) -> CateringRevenue:
        """
        Explicitly establish Catering Revenue eligibility.

        Eligibility is an explicit business operation. It is not
        inferred from Catering Event status.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REVENUE.ESTABLISH_ELIGIBILITY",
        )

        self._validate_entity(revenue)

        self._transition_workflow(
            revenue,
            CateringRevenueWorkflow.ELIGIBLE,
        )

        return super().update(revenue)

    def recognize(
        self,
        revenue: CateringRevenue,
        *,
        subject: Any,
    ) -> CateringRevenue:
        """
        Explicitly recognize an eligible Catering Revenue record.

        Recognition establishes the authoritative Catering revenue
        business fact. It does not create a Finance record.
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
        """
        Explicitly cancel DRAFT or ELIGIBLE Catering Revenue.
        """

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
