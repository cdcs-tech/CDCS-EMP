"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event Requirement repository.
"""

from __future__ import annotations

from sqlalchemy import false, select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import EventRequirement


class EventRequirementRepository(
    SQLAlchemyRepository[EventRequirement],
):
    """
    Repository for Catering Event Requirement entities.

    Provides persistence access for EventRequirement without
    owning Catering business rules or workflow transitions.
    """

    def __init__(self) -> None:
        """Initialize the Catering Event Requirement repository."""
        super().__init__(EventRequirement)

    def get_by_event_id(
        self,
        event_id: int,
    ) -> list[EventRequirement]:
        """Return all Event Requirements associated with an Event."""
        statement = select(EventRequirement).where(
            EventRequirement.event_id == event_id,
        )

        return list(
            db.session.execute(statement).scalars().all()
        )

    def get_by_id_for_update(
        self,
        requirement_id: int,
    ) -> EventRequirement | None:
        """Read and lock a requirement for a SQL Server transaction."""
        statement = (
            select(EventRequirement)
            .where(
                EventRequirement.id == requirement_id,
                EventRequirement.is_deleted == false(),
            )
            .with_hint(
                EventRequirement,
                "WITH (UPDLOCK, HOLDLOCK)",
                dialect_name="mssql",
            )
        )

        return db.session.execute(statement).scalar_one_or_none()


__all__ = [
    "EventRequirementRepository",
]
