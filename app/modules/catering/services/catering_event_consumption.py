"""Post physical stock consumption against a Catering Event Requirement."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import IntegrityError

from app.core.crud.exceptions import (
    EntityNotFoundException,
    EntityValidationException,
)
from app.modules.catering.models import (
    CateringEventConsumptionEvidence,
    StockMovement,
)


class CateringEventConsumptionService:
    """Atomically post an ISSUE movement and its consumption evidence."""

    def __init__(
        self,
        *,
        requirement_repository,
        consumption_evidence_repository,
        movement_service,
    ) -> None:
        self.requirement_repository = requirement_repository
        self.consumption_evidence_repository = (
            consumption_evidence_repository
        )
        self.movement_service = movement_service

    @staticmethod
    def _positive_quantity(value, label: str) -> Decimal:
        try:
            quantity = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise EntityValidationException(
                f"{label} must be a valid number."
            ) from exc

        if not quantity.is_finite() or quantity <= 0:
            raise EntityValidationException(
                f"{label} must be greater than zero."
            )

        return quantity

    @staticmethod
    def _unit(value) -> str:
        return (value or "").strip().casefold()

    @staticmethod
    def _normalized_key(value: str) -> str:
        if not isinstance(value, str):
            raise EntityValidationException(
                "An idempotency key is required."
            )

        key = value.strip()
        if not key:
            raise EntityValidationException(
                "An idempotency key is required."
            )

        if len(key) > 128:
            raise EntityValidationException(
                "The idempotency key cannot exceed 128 characters."
            )

        return key

    def _validate_requirement(
        self,
        *,
        requirement,
        event,
        quantity: Decimal,
        unit: str,
        location_id: int,
    ) -> None:
        """Validate current requirement details before any stock posting."""
        if requirement is None or requirement.is_deleted:
            raise EntityNotFoundException(
                "Event Requirement",
                getattr(requirement, "id", None),
            )

        if requirement.event_id != event.id:
            raise EntityValidationException(
                "The Event Requirement does not belong to this Event."
            )

        if requirement.status in {"DRAFT", "CANCELLED"}:
            raise EntityValidationException(
                "The Event Requirement is not eligible for consumption."
            )

        if requirement.stock_item_id is None:
            raise EntityValidationException(
                "The Event Requirement has no Inventory Stock Item."
            )

        if self._unit(unit) != self._unit(requirement.unit):
            raise EntityValidationException(
                "The consumption unit does not match the requirement."
            )

        required = self._positive_quantity(
            requirement.quantity,
            "Required quantity",
        )
        if quantity > required:
            raise EntityValidationException(
                "The issue would exceed the remaining "
                "Event Requirement quantity."
            )

        if (
            not isinstance(location_id, int)
            or isinstance(location_id, bool)
            or location_id <= 0
        ):
            raise EntityValidationException(
                "A valid Inventory location is required."
            )

    def _load_locked_requirement(self, requirement_id: int):
        """Load and lock the requirement inside the active transaction."""
        requirement = self.requirement_repository.get_by_id_for_update(
            requirement_id
        )

        if requirement is None or requirement.is_deleted:
            raise EntityNotFoundException(
                "Event Requirement",
                requirement_id,
            )

        return requirement

    def _find_existing(self, idempotency_key: str):
        return self.consumption_evidence_repository.get_by_idempotency_key(
            idempotency_key
        )

    def _validate_existing(
        self,
        *,
        evidence,
        requirement,
        quantity: Decimal,
        unit: str,
        location_id: int,
        reference: str,
    ):
        """Return matching evidence or reject reuse of its key."""
        movement = getattr(evidence, "stock_movement", None)
        if movement is None:
            movement = self.movement_service.get_by_reference(reference)

        try:
            evidence_quantity = Decimal(str(evidence.quantity))
            movement_quantity = (
                Decimal(str(movement.quantity))
                if movement is not None
                else None
            )
        except (InvalidOperation, TypeError, ValueError):
            evidence_quantity = None
            movement_quantity = None

        matches = (
            evidence.event_requirement_id == requirement.id
            and evidence_quantity == quantity
            and self._unit(evidence.unit) == self._unit(unit)
            and movement is not None
            and movement.id == evidence.stock_movement_id
            and movement.status == "POSTED"
            and movement.movement_type == "ISSUE"
            and movement.stock_item_id == requirement.stock_item_id
            and movement.location_id == location_id
            and movement_quantity == -quantity
        )

        if not matches:
            raise EntityValidationException(
                "The idempotency key was already used "
                "for a different operation."
            )

        return evidence

    def _consume_in_transaction(
        self,
        *,
        event,
        requirement_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
        subject,
        idempotency_key: str,
    ):
        requirement = self._load_locked_requirement(requirement_id)

        # Revalidate the locked row; preliminary validation cannot protect
        # against changes made by another transaction.
        self._validate_requirement(
            requirement=requirement,
            event=event,
            quantity=quantity,
            unit=unit,
            location_id=location_id,
        )

        reference = (
            f"CATERING-CONSUMPTION-{requirement.guid}-"
            f"{idempotency_key}"
        )

        # Recheck inside the transaction after acquiring the row lock.
        existing = self._find_existing(idempotency_key)
        if existing is not None:
            return self._validate_existing(
                evidence=existing,
                requirement=requirement,
                quantity=quantity,
                unit=unit,
                location_id=location_id,
                reference=reference,
            )

        evidence_records = (
            self.consumption_evidence_repository.get_by_requirement_id(
                requirement.id
            )
        )

        consumed = Decimal("0")
        for evidence in evidence_records:
            if getattr(evidence, "is_deleted", False):
                continue
            consumed += self._positive_quantity(
                evidence.quantity,
                "Recorded consumption quantity",
            )

        required = self._positive_quantity(
            requirement.quantity,
            "Required quantity",
        )

        if consumed + quantity > required:
            raise EntityValidationException(
                "The issue would exceed the remaining "
                "Event Requirement quantity."
            )

        movement = StockMovement(
            stock_item_id=requirement.stock_item_id,
            location_id=location_id,
            movement_type="ISSUE",
            status="DRAFT",
            quantity=-quantity,
            unit=requirement.unit,
            reference=reference,
            reason=(
                f"Catering Event {event.id}; "
                f"Event Requirement {requirement.id}"
            ),
            occurred_at=datetime.now(timezone.utc),
        )

        self.movement_service._authorize(
            subject,
            "CATERING.STOCK_MOVEMENT.POST",
        )
        self.movement_service._validate_movement_for_posting(movement)
        self.movement_service._validate_workflow_transition(movement)

        movement = self.movement_service.repository.add(movement)
        self.movement_service._apply_balance_effect(movement)

        movement.status = "POSTED"
        movement.posted_at = datetime.now(timezone.utc)
        movement = self.movement_service.repository.update(movement)

        evidence = CateringEventConsumptionEvidence(
            event_requirement_id=requirement.id,
            stock_movement_id=movement.id,
            quantity=quantity,
            unit=requirement.unit,
            idempotency_key=idempotency_key,
        )
        self.consumption_evidence_repository.add(evidence)

        return evidence

    def consume(
        self,
        *,
        event,
        requirement_id: int,
        location_id: int,
        quantity,
        unit: str,
        subject,
        idempotency_key: str,
    ):
        """Post consumption atomically and handle idempotent retries."""
        if event is None or getattr(event, "id", None) is None:
            raise EntityValidationException(
                "A persisted Catering Event is required."
            )

        key = self._normalized_key(idempotency_key)
        normalized_quantity = self._positive_quantity(
            quantity,
            "Consumption quantity",
        )

        # Preliminary validation preserves early rejection behavior.
        # The requirement is fetched and validated again under lock below.
        preliminary_requirement = self.requirement_repository.get_by_id(
            requirement_id
        )
        if preliminary_requirement is None or preliminary_requirement.is_deleted:
            raise EntityNotFoundException(
                "Event Requirement",
                requirement_id,
            )

        self._validate_requirement(
            requirement=preliminary_requirement,
            event=event,
            quantity=normalized_quantity,
            unit=unit,
            location_id=location_id,
        )

        reference = (
            f"CATERING-CONSUMPTION-{preliminary_requirement.guid}-{key}"
        )

        # Fast path for an already-committed retry. This is read-only;
        # a new operation still performs the authoritative lookup in the
        # transaction after acquiring the requirement lock.
        existing = self._find_existing(key)
        if existing is not None:
            return self._validate_existing(
                evidence=existing,
                requirement=preliminary_requirement,
                quantity=normalized_quantity,
                unit=unit,
                location_id=location_id,
                reference=reference,
            )

        # Reject already-known cumulative overconsumption before opening
        # the transaction. The authoritative check remains under the row lock.
        preliminary_evidence = (
            self.consumption_evidence_repository.get_by_requirement_id(
                preliminary_requirement.id
            )
        )

        preliminary_consumed = Decimal("0")
        for evidence in preliminary_evidence:
            if getattr(evidence, "is_deleted", False):
                continue
            preliminary_consumed += self._positive_quantity(
                evidence.quantity,
                "Recorded consumption quantity",
            )

        preliminary_required = self._positive_quantity(
            preliminary_requirement.quantity,
            "Required quantity",
        )

        if preliminary_consumed + normalized_quantity > preliminary_required:
            raise EntityValidationException(
                "The issue would exceed the remaining "
                "Event Requirement quantity."
            )

        try:
            with self.movement_service.transaction_manager.transaction():
                return self._consume_in_transaction(
                    event=event,
                    requirement_id=requirement_id,
                    location_id=location_id,
                    quantity=normalized_quantity,
                    unit=unit,
                    subject=subject,
                    idempotency_key=key,
                )
        except IntegrityError:
            # The transaction manager must roll back before this lookup.
            # A concurrent request may have committed the same key first.
            existing = self._find_existing(key)
            if existing is None:
                raise

            requirement = self.requirement_repository.get_by_id(
                requirement_id
            )
            if (
                requirement is None
                or requirement.is_deleted
                or requirement.event_id != event.id
            ):
                raise EntityValidationException(
                    "The Event Requirement does not belong to this Event."
                )

            self._validate_requirement(
                requirement=requirement,
                event=event,
                quantity=normalized_quantity,
                unit=unit,
                location_id=location_id,
            )

            reference = f"CATERING-CONSUMPTION-{requirement.guid}-{key}"
            return self._validate_existing(
                evidence=existing,
                requirement=requirement,
                quantity=normalized_quantity,
                unit=unit,
                location_id=location_id,
                reference=reference,
            )


__all__ = ["CateringEventConsumptionService"]
