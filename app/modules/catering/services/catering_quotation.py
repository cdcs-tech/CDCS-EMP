"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Quotation service.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from app.core.crud import CRUDService
from app.core.crud.exceptions import EntityValidationException
from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.core.workflow.base import WorkflowState
from app.modules.catering.models import (
    CateringQuotation,
    CateringQuotationLine,
    CateringEvent,
    Customer,
)
from app.modules.catering.repositories import CateringQuotationRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import CateringQuotationWorkflow


_MONEY_QUANTUM = Decimal("0.01")


class CateringQuotationService(CRUDService[CateringQuotation]):
    """
    Application service for Catering Quotation operations.

    The service owns quotation business validation, calculation,
    authorization, and lifecycle coordination.

    The quotation workflow owns lifecycle transition validity.

    Acceptance of a quotation deliberately does not mutate the
    associated Catering Event. Event confirmation coordination
    remains a separate business boundary.
    """

    def __init__(
        self,
        repository: CateringQuotationRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
        workflow: CateringQuotationWorkflow | None = None,
        customer_repository: SQLAlchemyRepository[Customer] | None = None,
        event_repository: SQLAlchemyRepository[CateringEvent] | None = None,
    ) -> None:
        super().__init__(
            repository or CateringQuotationRepository(),
            entity_name="CateringQuotation",
        )

        self.authorization_adapter = authorization_adapter
        self.workflow = workflow or CateringQuotationWorkflow()

        self.customer_repository = (
            customer_repository
            or SQLAlchemyRepository(Customer)
        )

        self.event_repository = (
            event_repository
            or SQLAlchemyRepository(CateringEvent)
        )

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering Quotation operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Catering Quotation operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    @staticmethod
    def _to_decimal(
        value: Decimal | int | float | str | None,
        *,
        field_name: str,
    ) -> Decimal:
        """
        Convert a monetary or quantity value to Decimal safely.

        String conversion is used for incoming numeric values to
        avoid binary floating-point arithmetic.
        """

        if value is None:
            raise EntityValidationException(
                f"{field_name} is required."
            )

        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise EntityValidationException(
                f"{field_name} must be a valid numeric value."
            ) from None

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        """
        Normalize a monetary value to two decimal places.
        """

        return value.quantize(
            _MONEY_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

    def _validate_references(
        self,
        quotation: CateringQuotation,
    ) -> None:
        """
        Validate the customer and event references.

        A quotation must reference existing Customer and Catering
        Event records, and both records must belong to the same
        customer context.
        """

        customer = self.customer_repository.get_by_id(
            quotation.customer_id
        )

        if customer is None:
            raise EntityValidationException(
                "Quotation customer does not exist."
            )

        event = self.event_repository.get_by_id(
            quotation.event_id
        )

        if event is None:
            raise EntityValidationException(
                "Quotation event does not exist."
            )

        if event.customer_id != quotation.customer_id:
            raise EntityValidationException(
                "Quotation customer must match the event customer."
            )

    def _validate_dates(
        self,
        quotation: CateringQuotation,
    ) -> None:
        """
        Validate the quotation validity period.
        """

        if quotation.quotation_date is None:
            raise EntityValidationException(
                "Quotation date is required."
            )

        if quotation.valid_until is None:
            raise EntityValidationException(
                "Quotation valid-until date is required."
            )

        if quotation.valid_until < quotation.quotation_date:
            raise EntityValidationException(
                "Quotation valid-until date cannot be earlier "
                "than the quotation date."
            )

    def _validate_line(
        self,
        line: CateringQuotationLine,
    ) -> Decimal:
        """
        Validate a quotation line and calculate its monetary total.

        Returns:
            The calculated line total rounded to two decimals.
        """

        if not line.description or not line.description.strip():
            raise EntityValidationException(
                "Quotation line description is required."
            )

        if not line.unit or not line.unit.strip():
            raise EntityValidationException(
                "Quotation line unit is required."
            )

        quantity = self._to_decimal(
            line.quantity,
            field_name="Quotation line quantity",
        )

        if quantity <= 0:
            raise EntityValidationException(
                "Quotation line quantity must be greater than zero."
            )

        unit_price = self._to_decimal(
            line.unit_price,
            field_name="Quotation line unit price",
        )

        if unit_price < 0:
            raise EntityValidationException(
                "Quotation line unit price cannot be negative."
            )

        line_total = self._money(
            quantity * unit_price
        )

        line.total_amount = line_total

        return line_total

    def _recalculate(
        self,
        quotation: CateringQuotation,
    ) -> None:
        """
        Validate quotation lines and recalculate all derived totals.

        Caller-supplied subtotal, total, and line totals are never
        trusted as authoritative values.
        """

        adjustment = self._to_decimal(
            quotation.adjustment_amount,
            field_name="Quotation adjustment amount",
        )

        adjustment = self._money(adjustment)
        quotation.adjustment_amount = adjustment

        subtotal = Decimal("0.00")

        for line in quotation.lines:
            subtotal += self._validate_line(line)

        subtotal = self._money(subtotal)

        quotation.subtotal = subtotal
        quotation.total_amount = self._money(
            subtotal + adjustment
        )

    def _validate_for_mutation(
        self,
        quotation: CateringQuotation,
    ) -> None:
        """
        Validate references, dates, and financial calculations before
        a quotation is persisted.
        """

        self._validate_references(quotation)
        self._validate_dates(quotation)
        self._recalculate(quotation)

    def _transition_workflow(
        self,
        quotation: CateringQuotation,
        target_state: str,
    ) -> WorkflowState:
        """
        Validate and apply a Catering Quotation workflow transition.

        The workflow owns lifecycle transition validity. The service
        applies the resulting state to the entity.
        """

        state = self.workflow.transition(
            quotation.status,
            target_state,
        )

        quotation.status = state.name

        return state

    def _require_draft(
        self,
        quotation: CateringQuotation,
    ) -> None:
        """
        Require the quotation to remain editable/deletable.
        """

        if quotation.status != CateringQuotationWorkflow.DRAFT:
            raise EntityValidationException(
                "Only DRAFT quotations can be modified or deleted."
            )

    def _require_lines_for_issue(
        self,
        quotation: CateringQuotation,
    ) -> None:
        """
        Require at least one quotation line before issuance.
        """

        if not quotation.lines:
            raise EntityValidationException(
                "A quotation must contain at least one line before it "
                "can be issued."
            )

    def create(
        self,
        entity: CateringQuotation,
        *,
        subject: Any,
    ) -> CateringQuotation:
        """
        Create a new Catering Quotation.

        New quotations must begin in DRAFT state.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.CREATE",
        )

        if entity.status != CateringQuotationWorkflow.DRAFT:
            raise EntityValidationException(
                "New quotations must be created in DRAFT status."
            )

        self._validate_for_mutation(entity)

        return super().create(entity)

    def update(
        self,
        entity: CateringQuotation,
        *,
        subject: Any,
    ) -> CateringQuotation:
        """
        Update an existing Catering Quotation.

        Only DRAFT quotations are editable.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.UPDATE",
        )

        persisted = self.get(entity.id)

        self._require_draft(persisted)

        if entity.status != CateringQuotationWorkflow.DRAFT:
            raise EntityValidationException(
                "Only DRAFT quotations can be updated."
            )

        self._validate_for_mutation(entity)

        return super().update(entity)

    def delete(
        self,
        entity_id: int,
        *,
        subject: Any,
    ) -> None:
        """
        Delete a Catering Quotation.

        Only DRAFT quotations can be deleted.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.DELETE",
        )

        quotation = self.get(entity_id)

        self._require_draft(quotation)

        self.repository.delete(quotation)

    def issue(
        self,
        quotation: CateringQuotation,
        *,
        subject: Any,
    ) -> CateringQuotation:
        """
        Issue a DRAFT quotation.

        Issuance requires at least one valid quotation line.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.ISSUE",
        )

        self._require_lines_for_issue(quotation)
        self._validate_for_mutation(quotation)

        self._transition_workflow(
            quotation,
            CateringQuotationWorkflow.ISSUED,
        )

        return super().update(quotation)

    def accept(
        self,
        quotation: CateringQuotation,
        *,
        subject: Any,
    ) -> CateringQuotation:
        """
        Accept an issued quotation.

        Acceptance does not mutate the associated Catering Event.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.ACCEPT",
        )

        self._transition_workflow(
            quotation,
            CateringQuotationWorkflow.ACCEPTED,
        )

        return super().update(quotation)

    def decline(
        self,
        quotation: CateringQuotation,
        *,
        subject: Any,
    ) -> CateringQuotation:
        """
        Decline an issued quotation.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.DECLINE",
        )

        self._transition_workflow(
            quotation,
            CateringQuotationWorkflow.DECLINED,
        )

        return super().update(quotation)

    def expire(
        self,
        quotation: CateringQuotation,
        *,
        subject: Any,
    ) -> CateringQuotation:
        """
        Explicitly expire an issued quotation.

        Expiry is an explicit business action in B4.2. No automatic
        date-driven expiry mechanism is introduced here.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_QUOTATION.EXPIRE",
        )

        self._transition_workflow(
            quotation,
            CateringQuotationWorkflow.EXPIRED,
        )

        return super().update(quotation)


__all__ = [
    "CateringQuotationService",
]
