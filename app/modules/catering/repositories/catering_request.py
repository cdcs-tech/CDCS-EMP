"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Request repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.modules.catering.models import CateringRequest


class CateringRequestRepository(
    SQLAlchemyRepository[CateringRequest],
):
    """
    Repository for Catering Request entities.

    Provides persistence access for CateringRequest without
    owning Catering business rules or workflow transitions.
    """

    def __init__(self) -> None:
        """
        Initialize the Catering Request repository.
        """

        super().__init__(
            CateringRequest
        )


__all__ = [
    "CateringRequestRepository",
]
