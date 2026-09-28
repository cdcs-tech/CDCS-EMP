"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.modules.catering.models import CateringEvent
from app.modules.catering.repositories import CateringEventRepository


class CateringEventService(CRUDService[CateringEvent]):
    """
    Application service for Catering Event persistence operations.

    Business lifecycle transitions and quotation-confirmation
    coordination are intentionally outside this service until
    their corresponding B3/B4 contracts are implemented.
    """

    def __init__(
        self,
        repository: CateringEventRepository | None = None,
    ) -> None:
        super().__init__(
            repository or CateringEventRepository(),
            entity_name="CateringEvent",
        )


__all__ = [
    "CateringEventService",
]
