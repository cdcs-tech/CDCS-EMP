"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Public platform infrastructure interface.
"""

from app.core.platform.config import (
    PlatformConfig,
    platform_config,
)

from app.core.platform.runtime import (
    RuntimeContext,
    runtime_context,
)

from app.core.platform.context import (
    RequestContext,
)

from app.core.platform.trace import (
    TraceContext,
    generate_id,
)

from app.core.platform.services import (
    ServiceRegistrationException,
    ServiceResolutionException,
    PlatformServiceContainer,
    platform_services,
)

from app.core.platform.exceptions import (
    CDCSPlatformException,
    PlatformConfigurationException,
    PlatformRuntimeException,
    PlatformContextException,
    PlatformServiceException,
    PlatformInfrastructureException,
)

from app.core.platform.logging import (
    DEFAULT_LOGGER_NAME,
    PlatformLogger,
    platform_logger,
)

from app.core.platform.metrics import (
    Metric,
    MetricsRegistry,
    MetricTimer,
    PlatformMetrics,
    metrics_registry,
    platform_metrics,
)

from app.core.platform.diagnostics import (
    DiagnosticStatus,
    DiagnosticSnapshot,
    RuntimeDiagnostics,
    runtime_diagnostics,
)

from app.core.platform.infrastructure import (
    PlatformInfrastructure,
    platform_infrastructure,
)

from app.core.platform.governance import (
    PlatformComponent,
    PlatformGovernance,
    platform_governance,
)

from app.core.platform.execution_observability import (
    PlatformExecutionObserver,
    platform_execution_observer,
)

__all__ = [
    "PlatformConfig",
    "platform_config",
    "RuntimeContext",
    "runtime_context",
    "RequestContext",
    "TraceContext",
    "generate_id",
    "ServiceRegistrationException",
    "ServiceResolutionException",
    "PlatformServiceContainer",
    "platform_services",
    "CDCSPlatformException",
    "PlatformConfigurationException",
    "PlatformRuntimeException",
    "PlatformContextException",
    "PlatformServiceException",
    "PlatformInfrastructureException",
    "DEFAULT_LOGGER_NAME",
    "PlatformLogger",
    "platform_logger",
    "Metric",
    "MetricsRegistry",
    "MetricTimer",
    "PlatformMetrics",
    "metrics_registry",
    "platform_metrics",
    "DiagnosticStatus",
    "DiagnosticSnapshot",
    "RuntimeDiagnostics",
    "runtime_diagnostics",
    "PlatformInfrastructure",
    "platform_infrastructure",
    "PlatformComponent",
    "PlatformGovernance",
    "platform_governance",
    "PlatformExecutionObserver",
    "platform_execution_observer",
]

