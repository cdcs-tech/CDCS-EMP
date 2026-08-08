"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Events.

Defines standard domain events generated
by the integration framework.
"""

from typing import Any, Optional

from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResult,
)

from app.core.events.base import (
    BaseEvent,
)


class IntegrationRequestEvent(BaseEvent):
    """
    Event generated when an integration request
    is initiated.
    """

    EVENT_NAME = "integration.request"

    def __init__(
        self,
        request: Optional[
            IntegrationRequest
        ] = None,
        subject: str = "",
    ):
        super().__init__()

        self.request = request
        self.subject = subject

    @property
    def event_name(self) -> str:
        """
        Return the unique event name.
        """

        return self.EVENT_NAME

    def metadata(self):
        """
        Return event metadata.
        """

        data = super().metadata()

        data.update(
            {
                "subject": self.subject,
            }
        )

        if self.request is not None:

            data.update(
                {
                    "request_id": (
                        self.request.request_id
                    ),
                    "provider": (
                        self.request.provider
                    ),
                    "operation": (
                        self.request.operation
                    ),
                }
            )

        return data


class IntegrationResultEvent(BaseEvent):
    """
    Event generated when an integration
    execution completes.
    """

    EVENT_NAME = "integration.result"

    def __init__(
        self,
        result: Optional[
            IntegrationResult
        ] = None,
        subject: str = "",
    ):
        super().__init__()

        self.result = result
        self.subject = subject

    @property
    def event_name(self) -> str:
        """
        Return the unique event name.
        """

        return self.EVENT_NAME

    def metadata(self):
        """
        Return event metadata.
        """

        data = super().metadata()

        data.update(
            {
                "subject": self.subject,
            }
        )

        if self.result is not None:

            data.update(
                {
                    "request_id": (
                        self.result.request.request_id
                    ),
                    "provider": (
                        self.result.provider
                    ),
                    "operation": (
                        self.result.operation
                    ),
                    "success": (
                        self.result.success
                    ),
                    "duration_ms": (
                        self.result.duration_ms
                    ),
                }
            )

        return data


class IntegrationFailureEvent(BaseEvent):
    """
    Event generated when integration execution
    fails before a normal IntegrationResult
    is available.
    """

    EVENT_NAME = "integration.failure"

    def __init__(
        self,
        request: Optional[
            IntegrationRequest
        ] = None,
        message: str = "",
        subject: str = "",
        metadata: Optional[
            dict[str, Any]
        ] = None,
    ):
        super().__init__()

        self.request = request
        self.message = message
        self.subject = subject

        self.details = (
            metadata or {}
        )

    @property
    def event_name(self) -> str:
        """
        Return the unique event name.
        """

        return self.EVENT_NAME

    def metadata(self):
        """
        Return event metadata.
        """

        data = super().metadata()

        data.update(
            {
                "message": self.message,
                "subject": self.subject,
                "details": self.details,
            }
        )

        if self.request is not None:

            data.update(
                {
                    "request_id": (
                        self.request.request_id
                    ),
                    "provider": (
                        self.request.provider
                    ),
                    "operation": (
                        self.request.operation
                    ),
                }
            )

        return data


__all__ = [
    "IntegrationRequestEvent",
    "IntegrationResultEvent",
    "IntegrationFailureEvent",
]
