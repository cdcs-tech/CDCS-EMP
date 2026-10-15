"""Repository for Event Requirement stock allocations."""

from __future__ import annotations

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.extensions import db
from app.modules.catering.models import EventRequirementStockAllocation


class EventRequirementStockAllocationRepository(
    SQLAlchemyRepository[EventRequirementStockAllocation],
):
    """Persistence operations specific to stock allocations."""

    def __init__(self) -> None:
        super().__init__(EventRequirementStockAllocation)

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> EventRequirementStockAllocation | None:
        """Return the allocation associated with an idempotency key."""

        statement = select(
            EventRequirementStockAllocation
        ).where(
            EventRequirementStockAllocation.idempotency_key
            == idempotency_key
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = ["EventRequirementStockAllocationRepository"]
