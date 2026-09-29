"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Event service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud import CRUDService
from app.modules.catering.models import CateringEvent
from app.modules.catering.repositories import CateringEventRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)


class CateringEventService(CRUDService[CateringEvent]):
    """
    Application service for Catering Event operations.

    Business lifecycle transitions and quotation-confirmation
    coordination are intentionally outside this service until
    their corresponding B3/B4 contracts are implemented.

    Protected business operations are authorized through the
    Catering authorization adapter at the service boundary.
    """

    def __init__(
        self,
        repository: CateringEventRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
    ) -> None:
        super().__init__(
            repository or CateringEventRepository(),
            entity_name="CateringEvent",
        )

        self.authorization_adapter = authorization_adapter

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering Event operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Catering Event operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def create(
        self,
        entity: CateringEvent,
        *,
        subject: Any,
    ) -> CateringEvent:
        """
        Create a Catering Event after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_EVENT.CREATE",
        )

        return super().create(entity)


__all__ = [
    "CateringEventService",
]
