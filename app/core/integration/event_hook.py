"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Event Hook.

Provides a controlled adapter between the
integration framework and the enterprise
event publishing infrastructure.
"""

from typing import Any, Optional

from app.core.events.publishers import (
    EventPublisher,
    event_publisher,
)

from app.core.integration.events import (
    IntegrationFailureEvent,
    IntegrationRequestEvent,
    IntegrationResultEvent,
)

from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResult,
)


class IntegrationEventHook:
    """
    Publishes integration lifecycle events
    through the enterprise event publisher.
    """

    def __init__(
        self,
        publisher: Optional[
            EventPublisher
        ] = None,
    ):
        """
        Initialize the integration event hook.
        """

        self.publisher = (
            publisher
            or event_publisher
        )

    def publish_request(
        self,
        request: IntegrationRequest,
        subject: str = "",
    ):
        """
        Publish an integration request event.
        """

        event = IntegrationRequestEvent(
            request=request,
            subject=subject,
        )

        return self.publisher.publish(
            event
        )

    def publish_result(
        self,
        result: IntegrationResult,
        subject: str = "",
    ):
        """
        Publish an integration result event.
        """

        event = IntegrationResultEvent(
            result=result,
            subject=subject,
        )

        return self.publisher.publish(
            event
        )

    def publish_failure(
        self,
        request: IntegrationRequest,
        message: str,
        subject: str = "",
        metadata: Optional[
            dict[str, Any]
        ] = None,
    ):
        """
        Publish an integration failure event.
        """

        event = IntegrationFailureEvent(
            request=request,
            message=message,
            subject=subject,
            metadata=metadata,
        )

        return self.publisher.publish(
            event
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationEventHook "
            f"publisher={self.publisher}>"
        )


integration_event_hook = (
    IntegrationEventHook()
)


__all__ = [
    "IntegrationEventHook",
    "integration_event_hook",
]

