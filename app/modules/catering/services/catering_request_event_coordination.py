"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Domain

Catering Request -> Event coordination service.
"""

from __future__ import annotations

from typing import Any

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models.catering_event import CateringEvent
from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)
from app.modules.catering.repositories.catering_request import (
    CateringRequestRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.security.permissions import (
    CATERING_EVENT_CREATE,
)


class CateringRequestEventCoordinationService:
    """
    Coordinate creation of an operational Catering Event from
    an existing Catering Request.

    This service owns only the Request -> Event application boundary.
    Event lifecycle progression remains owned by CateringEventService
    and CateringEventWorkflow.

    Quotation acceptance, confirmation, procurement, inventory,
    production, delivery, revenue, expense, and profitability
    processing remain outside this service.
    """

    CREATE_EVENT_PERMISSION = CATERING_EVENT_CREATE.name

    def __init__(
        self,
        *,
        request_repository: CateringRequestRepository | None = None,
        event_repository: CateringEventRepository | None = None,
        authorization_adapter: CateringAuthorizationAdapter | None = None,
    ) -> None:
        self.request_repository = (
            request_repository or CateringRequestRepository()
        )
        self.event_repository = (
            event_repository or CateringEventRepository()
        )
        self.authorization_adapter = authorization_adapter

    def _authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> None:
        """
        Authorize the requested operation.

        Authorization is fail-closed when no adapter is configured.
        """
        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required "
                "for protected Request-to-Event operations."
            )

        if not self.authorization_adapter.authorize(
            subject,
            permission_code,
        ):
            raise PermissionError(
                f"Not authorized for Catering operation: "
                f"{permission_code}"
            )

    def create_event_from_request(
        self,
        request_id: int,
        *,
        subject: Any,
        event_date=None,
        service_details=None,
        attendance=None,
        operational_notes=None,
    ) -> CateringEvent:
        """
        Create an operational Catering Event from a submitted Request.

        The resulting Event starts in REQUESTED state. The source
        Request is not modified.
        """
        self._authorize(
            subject,
            self.CREATE_EVENT_PERMISSION,
        )

        request = self.request_repository.get_by_id(request_id)

        if request is None:
            raise EntityNotFoundException(
                "Catering Request",
                request_id,
            )

        if request.status != "SUBMITTED":
            raise ValueError(
                "A Catering Event can only be created from a "
                "SUBMITTED Catering Request."
            )

        existing_event = self.event_repository.get_by_request_id(
            request.id
        )

        if existing_event is not None:
            raise ValueError(
                "A Catering Event already exists for Catering "
                f"Request {request.id}."
            )

        event = CateringEvent(
            request_id=request.id,
            customer_id=request.customer_id,
            event_date=(
                event_date
                if event_date is not None
                else request.service_date
            ),
            service_details=(
                service_details
                if service_details is not None
                else request.requested_service
            ),
            attendance=(
                attendance
                if attendance is not None
                else request.attendance
            ),
            operational_notes=(
                operational_notes
                if operational_notes is not None
                else request.notes
                or request.requirements
            ),
            status="REQUESTED",
        )

        return self.event_repository.add(event)


__all__ = [
    "CateringRequestEventCoordinationService",
]
