"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Procurement Finance commitment service.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.integration.exceptions import IntegrationDeliveryException
from app.core.integration.lifecycle import IntegrationLifecycle
from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResult,
)
from app.modules.procurement.integration.contracts import (
    FINANCE_INTEGRATION_PROVIDER,
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
    ProcurementFinancialEffectLine,
    ProcurementFinancialEffectRequest,
)
from app.modules.procurement.models import (
    ProcurementFinanceCommitment,
    PurchaseOrder,
)
from app.modules.procurement.repositories import (
    ProcurementFinanceCommitmentRepository,
)


class ProcurementFinanceCommitmentService:
    """
    Business service for durable Procurement Finance commitments.

    The service owns commitment registration, idempotency, lifecycle
    state transitions, Finance delivery, attempt tracking, and retry
    eligibility.

    Transaction ownership remains with the surrounding application
    transaction boundary. This service never commits or rolls back
    the database session.
    """

    PENDING = "PENDING"
    COMMITTED = "COMMITTED"
    RETRYABLE_FAILURE = "RETRYABLE_FAILURE"
    REJECTED = "REJECTED"

    _TERMINAL_STATES = {
        COMMITTED,
        REJECTED,
    }

    def __init__(
        self,
        repository: ProcurementFinanceCommitmentRepository | None = None,
        integration_lifecycle: IntegrationLifecycle | None = None,
        currency: str = "USD",
    ) -> None:
        self.repository = (
            repository
            or ProcurementFinanceCommitmentRepository()
        )

        self.integration_lifecycle = (
            integration_lifecycle
            or IntegrationLifecycle()
        )

        if not isinstance(
            self.integration_lifecycle,
            IntegrationLifecycle,
        ):
            raise TypeError(
                "integration_lifecycle must be an "
                "IntegrationLifecycle."
            )

        if not isinstance(currency, str) or not currency.strip():
            raise ValueError(
                "currency must be a non-empty string."
            )

        self.currency = currency.strip().upper()

    @classmethod
    def idempotency_key(
        cls,
        purchase_order: PurchaseOrder,
    ) -> str:
        """
        Build the deterministic business-operation idempotency key.
        """

        if not isinstance(
            purchase_order,
            PurchaseOrder,
        ):
            raise TypeError(
                "purchase_order must be a PurchaseOrder."
            )

        if (
            not isinstance(
                purchase_order.reference,
                str,
            )
            or not purchase_order.reference.strip()
        ):
            raise ValueError(
                "Purchase Order reference must be non-empty."
            )

        return (
            "procurement-commitment:"
            f"{purchase_order.reference}"
        )

    def register(
        self,
        purchase_order: PurchaseOrder,
    ) -> ProcurementFinanceCommitment:
        """
        Register durable Finance intent for an approved Purchase Order.

        Registration is idempotent. An existing commitment for the
        same Purchase Order or deterministic idempotency key is returned
        rather than creating a duplicate record.

        The commitment is created inside the caller's transaction.
        This service does not commit the transaction.
        """

        self._validate_purchase_order(
            purchase_order
        )

        if purchase_order.status != "APPROVED":
            raise ValueError(
                "Finance commitment can only be registered for "
                "an approved Purchase Order."
            )

        key = self.idempotency_key(
            purchase_order
        )

        existing = (
            self.repository.get_by_idempotency_key(
                key
            )
        )

        if existing is not None:
            return existing

        existing = (
            self.repository.get_by_purchase_order_id(
                purchase_order.id
            )
        )

        if existing is not None:
            return existing

        commitment = ProcurementFinanceCommitment(
            purchase_order_id=purchase_order.id,
            purchase_order_reference=(
                purchase_order.reference
            ),
            idempotency_key=key,
            status=self.PENDING,
            attempt_count=0,
        )

        return self.repository.add(
            commitment
        )

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> ProcurementFinanceCommitment | None:
        """
        Retrieve a commitment by its business-operation identity.
        """

        self._validate_idempotency_key(
            idempotency_key
        )

        return self.repository.get_by_idempotency_key(
            idempotency_key
        )

    def get_by_purchase_order_id(
        self,
        purchase_order_id: int,
    ) -> ProcurementFinanceCommitment | None:
        """
        Retrieve the commitment associated with a Purchase Order.
        """

        if not isinstance(
            purchase_order_id,
            int,
        ):
            raise TypeError(
                "purchase_order_id must be an integer."
            )

        return self.repository.get_by_purchase_order_id(
            purchase_order_id
        )

    def deliver(
        self,
        commitment: ProcurementFinanceCommitment,
        purchase_order: PurchaseOrder,
        *,
        subject: str = "",
        approved_at: datetime,
    ) -> IntegrationResult:
        """
        Deliver a registered Finance commitment.

        A new IntegrationRequest is created for every attempt while
        the commitment's durable idempotency key remains unchanged.

        Provider-declared failures become REJECTED.

        Integration delivery exceptions become RETRYABLE_FAILURE and
        are re-raised after the durable failure state is recorded.

        The approval timestamp is required because the Finance
        contract requires the actual Purchase Order approval time.
        """

        self._validate_commitment(
            commitment
        )

        self._validate_purchase_order(
            purchase_order
        )

        if commitment.purchase_order_id != purchase_order.id:
            raise ValueError(
                "Commitment does not belong to the supplied "
                "Purchase Order."
            )

        if commitment.status in self._TERMINAL_STATES:
            raise ValueError(
                "Terminal Finance commitments cannot be delivered."
            )

        if commitment.status == self.RETRYABLE_FAILURE:
            if not self.is_retry_eligible(
                commitment
            ):
                raise ValueError(
                    "Finance commitment is not currently "
                    "eligible for retry."
                )

        approval_timestamp = self._normalize_datetime(
            approved_at
        )

        payload = self._build_payload(
            purchase_order,
            approval_timestamp,
            commitment.idempotency_key,
        )

        request = IntegrationRequest(
            provider=FINANCE_INTEGRATION_PROVIDER,
            operation=FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
            payload=payload,
            metadata={
                "module": "PROCUREMENT",
                "purchase_order_id": purchase_order.id,
                "purchase_order_reference": (
                    purchase_order.reference
                ),
                "idempotency_key": (
                    commitment.idempotency_key
                ),
                "subject": subject,
            },
        )

        self._record_attempt(
            commitment
        )

        try:
            result = self.integration_lifecycle.execute(
                request,
                subject=subject,
            )
        except IntegrationDeliveryException as exc:
            self._record_retryable_failure(
                commitment,
                exc,
            )
            raise
        except Exception as exc:
            self._record_retryable_failure(
                commitment,
                exc,
            )
            raise

        if not isinstance(
            result,
            IntegrationResult,
        ):
            raise TypeError(
                "IntegrationLifecycle must return an "
                "IntegrationResult."
            )

        if result.success:
            self._record_committed(
                commitment,
                result,
            )
        else:
            self._record_rejected(
                commitment,
                result,
            )

        return result

    def retry(
        self,
        commitment: ProcurementFinanceCommitment,
        purchase_order: PurchaseOrder,
        *,
        subject: str = "",
        approved_at: datetime,
    ) -> IntegrationResult:
        """
        Retry an eligible technical Finance delivery failure.

        The same durable business idempotency key is reused, while the
        resulting IntegrationRequest receives a new request_id.
        """

        self._validate_commitment(
            commitment
        )

        if commitment.status != self.RETRYABLE_FAILURE:
            raise ValueError(
                "Only RETRYABLE_FAILURE commitments can be retried."
            )

        if not self.is_retry_eligible(
            commitment
        ):
            raise ValueError(
                "Finance commitment is not currently "
                "eligible for retry."
            )

        return self.deliver(
            commitment,
            purchase_order,
            subject=subject,
            approved_at=approved_at,
        )

    def is_retry_eligible(
        self,
        commitment: ProcurementFinanceCommitment,
        *,
        now: datetime | None = None,
    ) -> bool:
        """
        Determine whether a commitment is eligible for automatic retry.

        A retry is eligible only when:

        * status is RETRYABLE_FAILURE; and
        * next_retry_at is populated; and
        * next_retry_at is due.
        """

        self._validate_commitment(
            commitment
        )

        if commitment.status != self.RETRYABLE_FAILURE:
            return False

        if commitment.next_retry_at is None:
            return False

        current_time = self._normalize_datetime(
            now
            or datetime.now(timezone.utc)
        )

        next_retry = self._normalize_datetime(
            commitment.next_retry_at
        )

        return next_retry <= current_time

    def _record_attempt(
        self,
        commitment: ProcurementFinanceCommitment,
    ) -> None:
        """
        Record the beginning of one Finance delivery attempt.
        """

        commitment.attempt_count += 1
        commitment.last_attempted_at = (
            datetime.now(timezone.utc)
        )

        commitment.last_error = None
        commitment.last_response_message = None
        commitment.last_response_status_code = None

        self.repository.update(
            commitment
        )

    def _record_committed(
        self,
        commitment: ProcurementFinanceCommitment,
        result: IntegrationResult,
    ) -> None:
        """
        Record a successful Finance commitment.
        """

        response = result.response

        commitment.status = self.COMMITTED
        commitment.committed_at = datetime.now(
            timezone.utc
        )
        commitment.last_failure_at = None
        commitment.next_retry_at = None
        commitment.last_error = None

        if response is not None:
            commitment.last_response_message = (
                response.message
            )
            commitment.last_response_status_code = (
                response.status_code
            )

        self.repository.update(
            commitment
        )

    def _record_rejected(
        self,
        commitment: ProcurementFinanceCommitment,
        result: IntegrationResult,
    ) -> None:
        """
        Record a provider-declared business rejection.

        Provider-declared rejection is terminal and is therefore not
        eligible for automatic retry.
        """

        response = result.response

        commitment.status = self.REJECTED
        commitment.next_retry_at = None

        if response is not None:
            commitment.last_response_message = (
                response.message
            )
            commitment.last_response_status_code = (
                response.status_code
            )
            commitment.last_error = response.error

        self.repository.update(
            commitment
        )

    def _record_retryable_failure(
        self,
        commitment: ProcurementFinanceCommitment,
        exc: Exception,
    ) -> None:
        """
        Record a technical Finance delivery failure.
        """

        now = datetime.now(
            timezone.utc
        )

        commitment.status = self.RETRYABLE_FAILURE
        commitment.last_failure_at = now
        commitment.next_retry_at = now
        commitment.last_error = str(exc)

        self.repository.update(
            commitment
        )

    def _build_payload(
        self,
        purchase_order: PurchaseOrder,
        approved_at: datetime,
        idempotency_key: str,
    ) -> ProcurementFinancialEffectRequest:
        """
        Build the authoritative Finance integration payload.
        """

        purchase_request = (
            purchase_order.purchase_request
        )

        supplier = purchase_order.supplier

        lines = tuple(
            self._build_line(line)
            for line in purchase_order.lines
        )

        total_value = sum(
            (
                Decimal(str(line.total_amount))
                for line in purchase_order.lines
            ),
            Decimal("0"),
        )

        return ProcurementFinancialEffectRequest(
            purchase_order_reference=(
                purchase_order.reference
            ),
            purchase_request_reference=(
                purchase_request.reference
            ),
            supplier_reference=supplier.code,
            purchase_order_date=datetime.combine(
                purchase_order.order_date,
                datetime.min.time(),
                tzinfo=timezone.utc,
            ),
            approved_at=approved_at,
            currency=purchase_order.currency,
            total_procurement_value=total_value,
            purchase_order_lines=lines,
            idempotency_key=idempotency_key,
        )

    @staticmethod
    def _build_line(
        line: Any,
    ) -> ProcurementFinancialEffectLine:
        """
        Build one Finance integration line.
        """

        return ProcurementFinancialEffectLine(
            purchase_order_line_reference=str(
                line.id
            ),
            description=line.description,
            quantity=Decimal(str(line.quantity)),
            unit=line.unit,
            unit_price=Decimal(
                str(line.unit_price)
            ),
            line_amount=Decimal(
                str(line.total_amount)
            ),
        )

    @staticmethod
    def _validate_purchase_order(
        purchase_order: PurchaseOrder,
    ) -> None:
        """
        Validate the minimum Purchase Order contract required by
        the Finance commitment service.
        """

        if not isinstance(
            purchase_order,
            PurchaseOrder,
        ):
            raise TypeError(
                "purchase_order must be a PurchaseOrder."
            )

        if purchase_order.id is None:
            raise ValueError(
                "Purchase Order must have a persisted id."
            )

        if (
            not isinstance(
                purchase_order.reference,
                str,
            )
            or not purchase_order.reference.strip()
        ):
            raise ValueError(
                "Purchase Order reference must be non-empty."
            )

        if (
            not isinstance(purchase_order.currency, str)
            or purchase_order.currency not in {"USD", "SSP"}
        ):
            raise ValueError(
                "Purchase Order currency must be USD or SSP."
            )

    @staticmethod
    def _validate_commitment(
        commitment: ProcurementFinanceCommitment,
    ) -> None:
        """
        Validate the minimum durable commitment contract.
        """

        if not isinstance(
            commitment,
            ProcurementFinanceCommitment,
        ):
            raise TypeError(
                "commitment must be a ProcurementFinanceCommitment."
            )

        if commitment.id is None:
            raise ValueError(
                "Finance commitment must be persisted."
            )

        if commitment.status not in {
            ProcurementFinanceCommitmentService.PENDING,
            ProcurementFinanceCommitmentService.COMMITTED,
            ProcurementFinanceCommitmentService.RETRYABLE_FAILURE,
            ProcurementFinanceCommitmentService.REJECTED,
        }:
            raise ValueError(
                f"Unknown Finance commitment status: "
                f"{commitment.status}"
            )

    @staticmethod
    def _validate_idempotency_key(
        idempotency_key: str,
    ) -> None:
        """
        Validate a business-operation idempotency key.
        """

        if (
            not isinstance(
                idempotency_key,
                str,
            )
            or not idempotency_key.strip()
        ):
            raise ValueError(
                "idempotency_key must be a non-empty string."
            )

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        """
        Normalize naive datetimes to UTC while preserving aware
        datetimes.
        """

        if not isinstance(
            value,
            datetime,
        ):
            raise TypeError(
                "value must be a datetime."
            )

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value


__all__ = [
    "ProcurementFinanceCommitmentService",
]
