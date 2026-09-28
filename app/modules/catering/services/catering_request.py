"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Request service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.modules.catering.models import CateringRequest
from app.modules.catering.repositories import CateringRequestRepository


class CateringRequestService(CRUDService[CateringRequest]):
    """
    Application service for Catering Request persistence operations.

    Business lifecycle transitions and Request-to-Event coordination
    are intentionally outside this service until their corresponding
    B3/B4 contracts are implemented.
    """

    def __init__(
        self,
        repository: CateringRequestRepository | None = None,
    ) -> None:
        super().__init__(
            repository or CateringRequestRepository(),
            entity_name="CateringRequest",
        )


__all__ = [
    "CateringRequestService",
]
