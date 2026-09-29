"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Request service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud import CRUDService
from app.modules.catering.models import CateringRequest
from app.modules.catering.repositories import CateringRequestRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)


class CateringRequestService(CRUDService[CateringRequest]):
    """
    Application service for Catering Request operations.

    Business lifecycle transitions and Request-to-Event coordination
    are intentionally outside this service until their corresponding
    B3/B4 contracts are implemented.

    Protected business operations are authorized through the
    Catering authorization adapter at the service boundary.
    """

    def __init__(
        self,
        repository: CateringRequestRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
    ) -> None:
        super().__init__(
            repository or CateringRequestRepository(),
            entity_name="CateringRequest",
        )

        self.authorization_adapter = authorization_adapter

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize a protected Catering Request operation.

        Authorization is fail-closed when no adapter has been
        configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Catering Request operations."
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def create(
        self,
        entity: CateringRequest,
        *,
        subject: Any,
    ) -> CateringRequest:
        """
        Create a Catering Request after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REQUEST.CREATE",
        )

        return super().create(entity)

    def update(
        self,
        entity: CateringRequest,
        *,
        subject: Any,
    ) -> CateringRequest:
        """
        Update a Catering Request after authorization.
        """

        self._authorize(
            subject,
            "CATERING.CATERING_REQUEST.UPDATE",
        )

        return super().update(entity)


__all__ = [
    "CateringRequestService",
]
