"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event repository.
"""

from __future__ import annotations

from app.core.data.query import QueryOptions
from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.modules.catering.models import CateringEvent


class CateringEventRepository(
    SQLAlchemyRepository[CateringEvent],
):
    """
    Repository for Catering Event entities.

    Provides persistence access for CateringEvent without
    owning Catering business rules or workflow transitions.
    """

    def __init__(self) -> None:
        """Initialize the Catering Event repository."""
        super().__init__(CateringEvent)

    def get_by_request_id(
        self,
        request_id: int,
    ) -> CateringEvent | None:
        """
        Retrieve an existing Event associated with a Request.

        Returns the first matching Event, or None when no Event
        exists for the supplied Request ID.
        """
        events = self.get_all(
            QueryOptions(
                filters={
                    "request_id": request_id,
                },
                page=1,
                page_size=1,
                sort_by="id",
                sort_direction="asc",
            )
        )

        return events[0] if events else None


__all__ = [
    "CateringEventRepository",
]
