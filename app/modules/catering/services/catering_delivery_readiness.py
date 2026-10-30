from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.crud.exceptions import EntityValidationException


class CateringDeliveryReadinessService:
    def __init__(
        self,
        requirement_repository: Any,
        consumption_evidence_repository: Any,
        procurement_evidence_resolver: Any = None,
    ) -> None:
        self._requirement_repository = requirement_repository
        self._consumption_evidence_repository = consumption_evidence_repository
        self._procurement_evidence_resolver = procurement_evidence_resolver

    def ensure_delivery_ready(self, event: Any) -> None:
        if event is None or getattr(event, "id", None) is None:
            raise EntityValidationException(
                "A persisted Catering Event is required."
            )

        requirements = self._requirement_repository.get_by_event_id(event.id)

        if not requirements:
            raise EntityValidationException(
                "Catering Event has no requirements and cannot be delivered."
            )

        for requirement in requirements:
            self._ensure_requirement_ready(requirement)

    def _ensure_requirement_ready(self, requirement: Any) -> None:
        requirement_id = getattr(requirement, "id", None)

        if requirement is None or requirement_id is None:
            raise EntityValidationException(
                "A persisted Event Requirement is required."
            )

        if getattr(requirement, "is_deleted", False):
            raise EntityValidationException(
                "Deleted Event Requirements cannot be delivered."
            )

        stock_item_id = getattr(requirement, "stock_item_id", None)
        unit = getattr(requirement, "unit", None)

        if stock_item_id is None:
            raise EntityValidationException(
                "Event Requirement must have a valid stock item and unit."
            )

        if not unit or not str(unit).strip():
            raise EntityValidationException(
                "Event Requirement must have a valid unit."
            )

        try:
            required_quantity = self._decimal(
                getattr(requirement, "quantity", None)
            )
        except (InvalidOperation, TypeError, ValueError):
            raise EntityValidationException(
                "Event Requirement quantities are invalid."
            )

        if not required_quantity.is_finite() or required_quantity <= 0:
            raise EntityValidationException(
                "Event Requirement quantities are invalid."
            )

        fulfilment_type = str(
            getattr(requirement, "fulfilment_type", "") or ""
        ).strip().upper()

        if fulfilment_type == "INVENTORY":
            self._ensure_inventory_requirement_ready(
                requirement=requirement,
                required_quantity=required_quantity,
                unit=unit,
                stock_item_id=stock_item_id,
            )
            return

        if fulfilment_type == "PROCUREMENT":
            self._ensure_procurement_requirement_ready(
                requirement=requirement,
                required_quantity=required_quantity,
                unit=unit,
            )
            return

        raise EntityValidationException(
            "Event Requirement fulfilment type is invalid or unsupported."
        )

    def _ensure_inventory_requirement_ready(
        self,
        requirement: Any,
        required_quantity: Decimal,
        unit: str,
        stock_item_id: Any,
    ) -> None:
        """
        Preserve the existing Inventory physical-consumption validation.
        Procurement requirements must not pass through this method.
        """
        requirement_id = requirement.id

        evidence_records = (
            self._consumption_evidence_repository.get_by_requirement_id(
                requirement_id
            )
        )

        if not evidence_records:
            raise EntityValidationException(
                "Event Requirement has no physical-consumption evidence."
            )

        total_consumed = Decimal("0")

        for evidence in evidence_records:
            if getattr(evidence, "is_deleted", False):
                raise EntityValidationException(
                    "Deleted consumption evidence cannot satisfy an Event Requirement."
                )

            evidence_unit = getattr(evidence, "unit", None)

            if self._normalize_unit(evidence_unit) != self._normalize_unit(unit):
                raise EntityValidationException(
                    "Consumption evidence unit does not match the Event Requirement unit."
                )

            try:
                evidence_quantity = self._decimal(
                    getattr(evidence, "quantity", None)
                )
            except (InvalidOperation, TypeError, ValueError):
                raise EntityValidationException(
                    "Consumption evidence quantity is invalid."
                )

            if not evidence_quantity.is_finite() or evidence_quantity <= 0:
                raise EntityValidationException(
                    "Consumption evidence quantity must be positive."
                )

            movement = getattr(evidence, "stock_movement", None)

            if movement is None:
                raise EntityValidationException(
                    "Consumption evidence must reference a posted stock movement."
                )

            if getattr(movement, "is_deleted", False):
                raise EntityValidationException(
                    "Deleted Stock Movements cannot satisfy an Event Requirement."
                )

            movement_status = str(
                getattr(movement, "status", "") or ""
            ).strip().upper()

            if movement_status != "POSTED":
                raise EntityValidationException(
                    "Consumption evidence must reference a POSTED Stock Movement."
                )

            movement_type = str(
                getattr(movement, "movement_type", "") or ""
            ).strip().upper()

            if movement_type != "ISSUE":
                raise EntityValidationException(
                    "Consumption evidence must reference an ISSUE Stock Movement."
                )

            if getattr(movement, "stock_item_id", None) != stock_item_id:
                raise EntityValidationException(
                    "Consumption Stock Movement stock item does not match the Event Requirement."
                )

            movement_unit = getattr(movement, "unit", None)

            if self._normalize_unit(movement_unit) != self._normalize_unit(unit):
                raise EntityValidationException(
                    "Consumption Stock Movement unit does not match the Event Requirement."
                )

            try:
                movement_quantity = self._decimal(
                    getattr(movement, "quantity", None)
                )
            except (InvalidOperation, TypeError, ValueError):
                raise EntityValidationException(
                    "Consumption Stock Movement quantity is invalid."
                )

            if not movement_quantity.is_finite() or movement_quantity >= 0:
                raise EntityValidationException(
                    "Consumption Stock Movement quantity must be negative."
                )

            if abs(movement_quantity) != evidence_quantity:
                raise EntityValidationException(
                    "Consumption evidence quantity does not match its Stock Movement quantity."
                )

            total_consumed += evidence_quantity

        if total_consumed < required_quantity:
            raise EntityValidationException(
                "Event Requirement has insufficient physical consumption evidence."
            )

    def _ensure_procurement_requirement_ready(
        self,
        requirement: Any,
        required_quantity: Decimal,
        unit: str,
    ) -> None:
        """
        Validate Procurement fulfilment through posted receipt evidence.
        This path does not create or require physical-consumption evidence.
        """
        if self._procurement_evidence_resolver is None:
            raise EntityValidationException(
                "Procurement receipt evidence is unavailable."
            )

        try:
            receipt_status = (
                self._procurement_evidence_resolver.get_receipt_status(
                    requirement
                )
            )
        except EntityValidationException:
            raise
        except Exception as exc:
            raise EntityValidationException(
                "Procurement receipt evidence is unavailable."
            ) from exc

        if receipt_status is None or not getattr(
            receipt_status, "success", False
        ):
            raise EntityValidationException(
                "Procurement receipt evidence is unavailable or could not be validated."
            )

        if not getattr(receipt_status, "has_receipts", False):
            raise EntityValidationException(
                "Event Requirement has no qualifying posted Procurement receipt evidence."
            )

        receipt_count = getattr(receipt_status, "receipt_count", 0)

        if receipt_count is None or receipt_count <= 0:
            raise EntityValidationException(
                "Event Requirement has no qualifying posted Procurement receipt evidence."
            )

        receipt_unit = getattr(receipt_status, "unit", None)

        if self._normalize_unit(receipt_unit) != self._normalize_unit(unit):
            raise EntityValidationException(
                "Procurement receipt unit does not match the Event Requirement unit."
            )

        try:
            received_quantity = self._decimal(
                getattr(receipt_status, "received_quantity", None)
            )
        except (InvalidOperation, TypeError, ValueError):
            raise EntityValidationException(
                "Procurement receipt quantity is invalid."
            )

        if not received_quantity.is_finite() or received_quantity < 0:
            raise EntityValidationException(
                "Procurement receipt quantity is invalid."
            )

        if received_quantity < required_quantity:
            raise EntityValidationException(
                "Event Requirement has insufficient posted Procurement receipt quantity."
            )

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        if value is None:
            raise InvalidOperation

        return Decimal(str(value))

    @staticmethod
    def _normalize_unit(value: Any) -> str:
        return str(value or "").strip().casefold()
