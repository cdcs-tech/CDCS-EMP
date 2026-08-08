"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Lifecycle Orchestration.

Coordinates integration execution with
enterprise event and audit hooks.
"""

from typing import Any, Optional

from app.core.integration.audit import (
    IntegrationAuditHook,
    integration_audit_hook,
)

from app.core.integration.event_hook import (
    IntegrationEventHook,
    integration_event_hook,
)

from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResult,
)

from app.core.integration.service import (
    IntegrationService,
    integration_service,
)


class IntegrationLifecycle:
    """
    Coordinates the complete integration lifecycle.

    The lifecycle delegates actual integration
    execution to IntegrationService while
    independently coordinating event and audit
    hooks.
    """

    def __init__(
        self,
        service: Optional[
            IntegrationService
        ] = None,
        event_hook: Optional[
            IntegrationEventHook
        ] = None,
        audit_hook: Optional[
            IntegrationAuditHook
        ] = None,
    ):
        """
        Initialize the lifecycle orchestrator.
        """

        self.service = (
            service
            or integration_service
        )

        self.event_hook = (
            event_hook
            or integration_event_hook
        )

        self.audit_hook = (
            audit_hook
            or integration_audit_hook
        )


    def execute(
        self,
        request: IntegrationRequest,
        subject: str = "",
    ) -> IntegrationResult:
        """
        Execute the complete integration lifecycle.

        Lifecycle:

            Request
              ↓
            Event
              ↓
            Audit
              ↓
            Integration Service
              ↓
            Result / Failure
              ↓
            Event
              ↓
            Audit
        """

        # --------------------------------------------------
        # Request lifecycle hooks
        # --------------------------------------------------

        self.event_hook.publish_request(
            request,
            subject=subject,
        )

        self.audit_hook.record_request(
            request,
            subject=subject,
        )


        try:

            result = self.service.execute(
                request
            )

        except Exception as exc:

            message = str(exc)

            self.event_hook.publish_failure(
                request,
                message=message,
                subject=subject,
                metadata={
                    "exception": (
                        type(exc).__name__
                    )
                },
            )

            self.audit_hook.record_failure(
                request,
                message=message,
                subject=subject,
                metadata={
                    "exception": (
                        type(exc).__name__
                    )
                },
            )

            raise


        # --------------------------------------------------
        # Successful or completed result hooks
        # --------------------------------------------------

        self.event_hook.publish_result(
            result,
            subject=subject,
        )

        self.audit_hook.record_result(
            result,
            subject=subject,
        )

        return result


    def execute_many(
        self,
        requests: list[
            IntegrationRequest
        ],
        subject: str = "",
    ) -> list[
        IntegrationResult
    ]:
        """
        Execute multiple integration requests
        sequentially through the lifecycle.
        """

        results = []

        for request in requests:

            results.append(
                self.execute(
                    request,
                    subject=subject,
                )
            )

        return results


    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationLifecycle "
            f"service={self.service} "
            f"event_hook={self.event_hook} "
            f"audit_hook={self.audit_hook}>"
        )


integration_lifecycle = (
    IntegrationLifecycle()
)


__all__ = [
    "IntegrationLifecycle",
    "integration_lifecycle",
]

