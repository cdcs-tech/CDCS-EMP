"""Inventory allocation service for Catering Event Requirements."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.modules.catering.models import EventRequirementStockAllocation
from app.modules.catering.models.stock_balance import StockBalance
from app.modules.catering.repositories.balance import StockBalanceRepository
from app.modules.catering.repositories.event_requirement import (
    EventRequirementRepository,
)
from app.modules.catering.repositories.event_requirement_stock_allocation import (
    EventRequirementStockAllocationRepository,
)
from app.modules.catering.repositories.stock_item import StockItemRepository


class EventRequirementStockAllocationService:
    """Track reservations of existing inventory for catering requirements.

    Allocations reserve quantities logically. They do not create stock
    movements, reduce physical balances, or prove procurement fulfilment.

    This service does not claim concurrency-safe reservation until the
    database-specific locking and transaction strategy is verified.
    """

    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    ALLOCATABLE_REQUIREMENT_STATUS = "IDENTIFIED"

    def __init__(
        self,
        repository: Any | None = None,
        balance_repository: Any | None = None,
        requirement_repository: Any | None = None,
        stock_item_repository: Any | None = None,
    ) -> None:
        self.repository = (
            repository
            if repository is not None
            else EventRequirementStockAllocationRepository()
        )
        self.balance_repository = (
            balance_repository
            if balance_repository is not None
            else StockBalanceRepository()
        )
        self.requirement_repository = (
            requirement_repository
            if requirement_repository is not None
            else EventRequirementRepository()
        )
        self.stock_item_repository = (
            stock_item_repository
            if stock_item_repository is not None
            else StockItemRepository()
        )

    @staticmethod
    def _positive_quantity(value: Any) -> Decimal:
        """Convert a quantity to a finite positive Decimal."""

        try:
            quantity = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(
                "Allocation quantity must be positive."
            ) from exc

        if not quantity.is_finite() or quantity <= 0:
            raise ValueError("Allocation quantity must be positive.")

        if quantity.as_tuple().exponent < -3:
            raise ValueError(
                "Allocation quantity cannot exceed three decimal places."
            )

        return quantity

    @staticmethod
    def _required_text(value: str | None, field: str) -> str:
        """Validate and normalize required text."""

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Allocation {field} is required.")

        return value.strip()

    @staticmethod
    def _normalize_unit(value: Any, field: str) -> str:
        """Validate a unit and normalize whitespace and letter case."""

        unit = EventRequirementStockAllocationService._required_text(
            value,
            field,
        )
        return unit.casefold()

    @staticmethod
    def _same_request(
        allocation: EventRequirementStockAllocation,
        *,
        event_requirement_id: int,
        stock_item_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
    ) -> bool:
        """Determine whether an existing idempotency record matches."""

        try:
            existing_quantity = Decimal(str(allocation.quantity))
        except (InvalidOperation, TypeError, ValueError):
            return False

        return (
            allocation.event_requirement_id == event_requirement_id
            and allocation.stock_item_id == stock_item_id
            and allocation.location_id == location_id
            and existing_quantity == quantity
            and isinstance(allocation.unit, str)
            and allocation.unit.strip().casefold() == unit.casefold()
        )

    def _existing_idempotent_result(
        self,
        *,
        idempotency_key: str,
        event_requirement_id: int,
        stock_item_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
    ) -> EventRequirementStockAllocation | None:
        """Return an identical prior request or reject key reuse."""

        existing = self.repository.get_by_idempotency_key(idempotency_key)

        if existing is None:
            return None

        if not self._same_request(
            existing,
            event_requirement_id=event_requirement_id,
            stock_item_id=stock_item_id,
            location_id=location_id,
            quantity=quantity,
            unit=unit,
        ):
            raise ValueError(
                "Idempotency key was already used for a different allocation."
            )

        return existing

    def _active_quantity(
        self,
        *,
        stock_item_id: int | None = None,
        location_id: int | None = None,
        event_requirement_id: int | None = None,
    ) -> Decimal:
        """Sum active allocation quantities matching the supplied filters."""

        statement = db.session.query(
            func.coalesce(
                func.sum(EventRequirementStockAllocation.quantity),
                0,
            )
        ).filter(
            EventRequirementStockAllocation.status == self.ACTIVE,
        )

        if stock_item_id is not None:
            statement = statement.filter(
                EventRequirementStockAllocation.stock_item_id
                == stock_item_id,
            )

        if location_id is not None:
            statement = statement.filter(
                EventRequirementStockAllocation.location_id == location_id,
            )

        if event_requirement_id is not None:
            statement = statement.filter(
                EventRequirementStockAllocation.event_requirement_id
                == event_requirement_id,
            )

        value = statement.scalar()
        return Decimal(str(value or 0))

    def _validate_requirement(
        self,
        *,
        event_requirement_id: int,
        stock_item_id: int,
        unit: str,
    ) -> Any:
        """Validate requirement existence, lifecycle, item mapping and unit."""

        requirement = self.requirement_repository.get_by_id(
            event_requirement_id,
        )
        if requirement is None:
            raise ValueError("Event Requirement does not exist.")

        if getattr(requirement, "status", None) != (
            self.ALLOCATABLE_REQUIREMENT_STATUS
        ):
            raise ValueError(
                "Event Requirement must be IDENTIFIED before stock allocation."
            )

        if getattr(requirement, "stock_item_id", None) != stock_item_id:
            raise ValueError(
                "Stock Item does not match the Event Requirement mapping."
            )

        requirement_unit = self._normalize_unit(
            getattr(requirement, "unit", None),
            "Event Requirement unit",
        )
        if requirement_unit != unit.casefold():
            raise ValueError(
                "Allocation unit does not match the Event Requirement unit."
            )

        try:
            required_quantity = Decimal(str(requirement.quantity))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(
                "Event Requirement quantity is invalid."
            ) from exc

        if not required_quantity.is_finite() or required_quantity <= 0:
            raise ValueError(
                "Event Requirement quantity must be positive."
            )

        return requirement

    def _validate_stock_item_unit(
        self,
        *,
        stock_item_id: int,
        unit: str,
    ) -> None:
        """Ensure the Stock Item's Product uses the allocation unit."""

        stock_item = self.stock_item_repository.get_by_id(stock_item_id)
        if stock_item is None:
            raise ValueError("Stock Item does not exist.")

        product = getattr(stock_item, "product", None)
        if product is None:
            raise ValueError(
                "Stock Item has no associated Product for unit validation."
            )

        product_unit = self._normalize_unit(
            getattr(product, "unit", None),
            "Product unit",
        )
        if product_unit != unit.casefold():
            raise ValueError(
                "Allocation unit does not match the Stock Item Product unit."
            )

    def allocate(
        self,
        *,
        event_requirement_id: int,
        stock_item_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
        idempotency_key: str,
    ) -> EventRequirementStockAllocation:
        """Allocate available stock to a requirement.

        The operation uses a savepoint so a failed insert does not explicitly
        roll back the caller's entire session. A unique-key conflict is checked
        for an identical prior request before an error is returned.

        Database-level concurrency protection for stock availability must be
        implemented and verified separately before concurrent use.
        """

        amount = self._positive_quantity(quantity)
        normalized_unit = self._required_text(unit, "unit")
        key = self._required_text(idempotency_key, "idempotency key")

        existing = self._existing_idempotent_result(
            idempotency_key=key,
            event_requirement_id=event_requirement_id,
            stock_item_id=stock_item_id,
            location_id=location_id,
            quantity=amount,
            unit=normalized_unit,
        )
        if existing is not None:
            return existing

        requirement = self._validate_requirement(
            event_requirement_id=event_requirement_id,
            stock_item_id=stock_item_id,
            unit=normalized_unit,
        )

        self._validate_stock_item_unit(
            stock_item_id=stock_item_id,
            unit=normalized_unit,
        )

        balance = self.balance_repository.get_by_stock_item_and_location(
            stock_item_id,
            location_id,
        )
        if balance is None:
            raise ValueError(
                "No stock balance exists at the requested location."
            )

        physical_quantity = Decimal(str(balance.quantity))
        if not physical_quantity.is_finite() or physical_quantity < 0:
            raise ValueError("Stock balance quantity is invalid.")

        allocated_for_item_location = self._active_quantity(
            stock_item_id=stock_item_id,
            location_id=location_id,
        )
        available_quantity = (
            physical_quantity - allocated_for_item_location
        )

        if amount > available_quantity:
            raise ValueError("Insufficient unallocated stock.")

        requirement_quantity = Decimal(str(requirement.quantity))
        already_allocated_for_requirement = self._active_quantity(
            event_requirement_id=event_requirement_id,
        )
        remaining_requirement_quantity = (
            requirement_quantity - already_allocated_for_requirement
        )

        if amount > remaining_requirement_quantity:
            raise ValueError(
                "Allocation exceeds the Event Requirement's remaining quantity."
            )

        allocation = EventRequirementStockAllocation(
            event_requirement_id=event_requirement_id,
            stock_item_id=stock_item_id,
            location_id=location_id,
            quantity=amount,
            unit=normalized_unit,
            idempotency_key=key,
            status=self.ACTIVE,
        )

        try:
            with db.session.begin_nested():
                self.repository.add(allocation)
                db.session.flush()
        except IntegrityError as exc:
            # The nested transaction handles the failed savepoint. Do not
            # explicitly roll back the caller's entire database session.
            existing = self._existing_idempotent_result(
                idempotency_key=key,
                event_requirement_id=event_requirement_id,
                stock_item_id=stock_item_id,
                location_id=location_id,
                quantity=amount,
                unit=normalized_unit,
            )
            if existing is not None:
                return existing

            raise ValueError(
                "Allocation conflicted with another transaction or "
                "a database constraint."
            ) from exc

        return allocation

    def release(
        self,
        *,
        allocation_id: int,
    ) -> EventRequirementStockAllocation:
        """Release an active allocation without changing physical stock."""

        allocation = self.repository.get_by_id(allocation_id)
        if allocation is None:
            raise ValueError("Stock allocation does not exist.")

        if allocation.status == self.RELEASED:
            return allocation

        if allocation.status != self.ACTIVE:
            raise ValueError(
                "Stock allocation has an invalid lifecycle status."
            )

        allocation.status = self.RELEASED
        self.repository.update(allocation)
        db.session.flush()

        return allocation


__all__ = ["EventRequirementStockAllocationService"]
