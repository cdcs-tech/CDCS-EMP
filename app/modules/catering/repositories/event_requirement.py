"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event Requirement repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
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
        """
        Initialize the Catering Event Requirement repository.
        """

        super().__init__(
            EventRequirement
        )


__all__ = [
    "EventRequirementRepository",
]
