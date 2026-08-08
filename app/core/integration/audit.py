"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Audit Hook.

Provides standardized integration activity
audit records using the CDCS-EMP security
audit framework.
"""

from typing import Optional

from app.core.integration.models import (
    IntegrationRequest,
    IntegrationResult,
)

from app.core.security.audit import (
    SecurityAuditEvent,
)

from app.core.security.audit_registry import (
    audit_registry,
)


class IntegrationAuditHook:
    """
    Integration-to-security audit adapter.

    Converts integration activity into
    SecurityAuditEvent objects.
    """

    EVENT_TYPE = "INTEGRATION"

    def __init__(
        self,
        registry=None,
    ):
        """
        Initialize the audit hook.
        """

        self.registry = (
            registry
            or audit_registry
        )


    def record_request(
        self,
        request: IntegrationRequest,
        subject: str = "",
    ) -> SecurityAuditEvent:
        """
        Record an integration request.
        """

        event = SecurityAuditEvent(
            event_type=(
                f"{self.EVENT_TYPE}_REQUEST"
            ),
            subject=subject,
            resource=request.provider,
            action=request.operation,
            result="SUCCESS",
            message=(
                "Integration request initiated."
            ),
            metadata={
                "request_id": (
                    request.request_id
                ),
                "provider": (
                    request.provider
                ),
                "operation": (
                    request.operation
                ),
            },
        )

        self.registry.record(
            event
        )

        return event


    def record_result(
        self,
        result: IntegrationResult,
        subject: str = "",
    ) -> SecurityAuditEvent:
        """
        Record an integration result.
        """

        audit_result = (
            "SUCCESS"
            if result.success
            else "FAILED"
        )

        event = SecurityAuditEvent(
            event_type=(
                f"{self.EVENT_TYPE}_RESULT"
            ),
            subject=subject,
            resource=result.provider,
            action=result.operation,
            result=audit_result,
            message=(
                "Integration execution completed."
                if result.success
                else
                "Integration execution failed."
            ),
            metadata={
                "request_id": (
                    result.request.request_id
                ),
                "provider": (
                    result.provider
                ),
                "operation": (
                    result.operation
                ),
                "duration_ms": (
                    result.duration_ms
                ),
            },
        )

        self.registry.record(
            event
        )

        return event


    def record_failure(
        self,
        request: IntegrationRequest,
        message: str,
        subject: str = "",
        metadata: Optional[dict] = None,
    ) -> SecurityAuditEvent:
        """
        Record an integration failure that
        occurs before an IntegrationResult exists.
        """

        event_metadata = {
            "request_id": (
                request.request_id
            ),
            "provider": (
                request.provider
            ),
            "operation": (
                request.operation
            ),
        }

        if metadata:
            event_metadata.update(
                metadata
            )

        event = SecurityAuditEvent(
            event_type=(
                f"{self.EVENT_TYPE}_FAILURE"
            ),
            subject=subject,
            resource=request.provider,
            action=request.operation,
            result="FAILED",
            message=message,
            metadata=event_metadata,
        )

        self.registry.record(
            event
        )

        return event


    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<IntegrationAuditHook "
            f"registry={self.registry}>"
        )


integration_audit_hook = (
    IntegrationAuditHook()
)

