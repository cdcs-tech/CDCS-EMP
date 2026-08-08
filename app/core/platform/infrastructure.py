"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Integrated Platform Infrastructure Facade.

Provides a unified access point to the
core platform infrastructure services.
"""

from typing import Optional

from app.core.platform.context import (
    RequestContext,
)

from app.core.platform.diagnostics import (
    RuntimeDiagnostics,
)

from app.core.platform.logging import (
    PlatformLogger,
)

from app.core.platform.metrics import (
    PlatformMetrics,
)

from app.core.platform.runtime import (
    RuntimeContext,
    runtime_context,
)

from app.core.platform.services import (
    PlatformServiceContainer,
    platform_services,
)


class PlatformInfrastructure:
    """
    Unified platform infrastructure facade.

    Coordinates access to runtime context,
    request context, service management,
    logging, metrics and diagnostics.
    """

    def __init__(
        self,
        *,
        runtime: Optional[
            RuntimeContext
        ] = None,
        services: Optional[
            PlatformServiceContainer
        ] = None,
        logger: Optional[
            PlatformLogger
        ] = None,
        metrics: Optional[
            PlatformMetrics
        ] = None,
        diagnostics: Optional[
            RuntimeDiagnostics
        ] = None,
    ):
        """
        Initialize platform infrastructure.
        """

        self.runtime = (
            runtime
            or runtime_context
        )

        self.services = (
            services
            or platform_services
        )

        self.logger = (
            logger
            or PlatformLogger()
        )

        self.metrics = (
            metrics
            or PlatformMetrics()
        )

        self.diagnostics = (
            diagnostics
            or RuntimeDiagnostics(
                service_container=self.services,
                metrics=self.metrics,
            )
        )

    def create_request_context(
        self,
        **kwargs,
    ) -> RequestContext:
        """
        Create a request context using
        the active runtime context.
        """

        return RequestContext(
            runtime=self.runtime,
            **kwargs,
        )

    def health_check(
        self,
        context: Optional[
            RequestContext
        ] = None,
    ):
        """
        Perform a platform health check.

        If no request context is supplied,
        a default context is created.
        """

        context = (
            context
            or self.create_request_context()
        )

        return self.diagnostics.check(
            context
        )

    def is_healthy(
        self,
        context: Optional[
            RequestContext
        ] = None,
    ) -> bool:
        """
        Determine whether the platform
        infrastructure is healthy.
        """

        context = (
            context
            or self.create_request_context()
        )

        return self.diagnostics.is_healthy(
            context
        )

    def service(
        self,
        name: str,
    ):
        """
        Resolve a registered platform service.
        """

        return self.services.get(
            name
        )

    def register_service(
        self,
        name: str,
        service,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a platform service.
        """

        self.services.register(
            name,
            service,
            replace=replace,
        )

    def log_context(
        self,
        message: str,
        context: RequestContext,
        *,
        level: str = "info",
        **extra,
    ) -> None:
        """
        Log a message using the request context.
        """

        log_method = getattr(
            self.logger,
            level,
            None,
        )

        if log_method is None:
            raise ValueError(
                f"Unsupported log level: "
                f"{level}"
            )

        log_method(
            message,
            context=context,
            **extra,
        )

    def increment_metric(
        self,
        name: str,
        amount: float = 1.0,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **labels,
    ):
        """
        Increment a platform metric.
        """

        return self.metrics.increment(
            name,
            amount,
            context=context,
            **labels,
        )

    def metric_timer(
        self,
        name: str,
        *,
        context: Optional[
            RequestContext
        ] = None,
        **labels,
    ):
        """
        Create a platform metric timer.
        """

        return self.metrics.timer(
            name,
            context=context,
            **labels,
        )

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            "<PlatformInfrastructure "
            f"environment="
            f"{self.runtime.environment!r}>"
        )


platform_infrastructure = (
    PlatformInfrastructure()
)


__all__ = [
    "PlatformInfrastructure",
    "platform_infrastructure",
]
