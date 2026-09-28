"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event repository.
"""

from __future__ import annotations

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
        """
        Initialize the Catering Event repository.
        """

        super().__init__(
            CateringEvent
        )


__all__ = [
    "CateringEventRepository",
]
