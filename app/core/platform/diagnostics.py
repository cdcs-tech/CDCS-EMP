"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Runtime Diagnostics Foundation.

Provides centralized runtime inspection
and diagnostic snapshots for the platform.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from app.core.platform.context import (
    RequestContext,
)

from app.core.platform.metrics import (
    PlatformMetrics,
)

from app.core.platform.services import (
    PlatformServiceContainer,
)


class DiagnosticStatus:
    """
    Standard diagnostic status values.
    """

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    UNHEALTHY = "UNHEALTHY"


class DiagnosticSnapshot:
    """
    Represents a point-in-time platform
    diagnostic snapshot.
    """

    def __init__(
        self,
        *,
        status: str,
        environment: str,
        application_name: str,
        application_version: str,
        service_count: int,
        metric_count: int,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        details: Optional[
            dict[str, Any]
        ] = None,
    ):
        self.status = status
        self.environment = environment
        self.application_name = (
            application_name
        )
        self.application_version = (
            application_version
        )
        self.service_count = service_count
        self.metric_count = metric_count
        self.request_id = request_id
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self.details = dict(
            details or {}
        )
        self.timestamp = (
            datetime.now(timezone.utc)
        )

    def is_healthy(self) -> bool:
        """
        Determine whether the snapshot is healthy.
        """

        return (
            self.status
            == DiagnosticStatus.HEALTHY
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Return the diagnostic snapshot
        as a dictionary.
        """

        return {
            "status": self.status,
            "environment": self.environment,
            "application_name": (
                self.application_name
            ),
            "application_version": (
                self.application_version
            ),
            "service_count": (
                self.service_count
            ),
            "metric_count": (
                self.metric_count
            ),
            "request_id": self.request_id,
            "correlation_id": (
                self.correlation_id
            ),
            "trace_id": self.trace_id,
            "timestamp": self.timestamp,
            "details": dict(
                self.details
            ),
        }

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<DiagnosticSnapshot "
            f"status={self.status!r} "
            f"environment="
            f"{self.environment!r} "
            f"services="
            f"{self.service_count} "
            f"metrics="
            f"{self.metric_count}>"
        )


class RuntimeDiagnostics:
    """
    Central runtime diagnostics service.
    """

    def __init__(
        self,
        *,
        service_container: Optional[
            PlatformServiceContainer
        ] = None,
        metrics: Optional[
            PlatformMetrics
        ] = None,
    ):
        self.service_container = (
            service_container
            or PlatformServiceContainer()
        )

        self.metrics = (
            metrics
            or PlatformMetrics()
        )

    def check(
        self,
        context: RequestContext,
    ) -> DiagnosticSnapshot:
        """
        Generate a runtime diagnostic snapshot.
        """

        context.validate()

        status = (
            DiagnosticStatus.HEALTHY
        )

        details = {
            "runtime_valid": True,
            "context_valid": True,
        }

        return DiagnosticSnapshot(
            status=status,
            environment=context.environment,
            application_name=(
                context.application_name
            ),
            application_version=(
                context.application_version
            ),
            service_count=(
                self.service_container.count()
            ),
            metric_count=(
                self.metrics.registry.count()
            ),
            request_id=context.request_id,
            correlation_id=(
                context.correlation_id
            ),
            trace_id=context.trace_id,
            details=details,
        )

    def status(
        self,
        context: RequestContext,
    ) -> str:
        """
        Return the current runtime status.
        """

        return self.check(
            context
        ).status

    def is_healthy(
        self,
        context: RequestContext,
    ) -> bool:
        """
        Determine whether the runtime is healthy.
        """

        return self.check(
            context
        ).is_healthy()

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "<RuntimeDiagnostics>"
        )


runtime_diagnostics = (
    RuntimeDiagnostics()
)


__all__ = [
    "DiagnosticStatus",
    "DiagnosticSnapshot",
    "RuntimeDiagnostics",
    "runtime_diagnostics",
]
