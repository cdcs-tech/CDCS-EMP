"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Integration Tests

Final integration and regression tests for
the platform foundation.
"""

from app.core.platform import (
    DiagnosticStatus,
    PlatformComponent,
    PlatformConfig,
    PlatformInfrastructure,
    PlatformGovernance,
    PlatformMetrics,
    PlatformServiceContainer,
    RequestContext,
    RuntimeContext,
    RuntimeDiagnostics,
)


def create_platform():

    runtime = RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )

    services = PlatformServiceContainer()

    metrics = PlatformMetrics()

    diagnostics = RuntimeDiagnostics(
        service_container=services,
        metrics=metrics,
    )

    infrastructure = PlatformInfrastructure(
        runtime=runtime,
        services=services,
        metrics=metrics,
        diagnostics=diagnostics,
    )

    return infrastructure


def test_complete_platform_foundation():

    platform = create_platform()

    assert (
        platform.runtime.environment
        == "testing"
    )

    assert (
        platform.services
        is not None
    )

    assert (
        platform.metrics
        is not None
    )

    assert (
        platform.diagnostics
        is not None
    )


def test_request_context_flows_through_platform():

    platform = create_platform()

    context = (
        platform.create_request_context(
            user_id="user-001",
            module_name="finance",
            operation="create_invoice",
        )
    )

    assert isinstance(
        context,
        RequestContext,
    )

    assert (
        context.environment
        == "testing"
    )

    assert (
        context.user_id
        == "user-001"
    )

    assert (
        context.module_name
        == "finance"
    )

    assert (
        context.operation
        == "create_invoice"
    )


def test_platform_health():

    platform = create_platform()

    context = (
        platform.create_request_context(
            module_name="platform",
            operation="health_check",
        )
    )

    snapshot = platform.health_check(
        context
    )

    assert (
        snapshot.status
        == DiagnosticStatus.HEALTHY
    )

    assert (
        snapshot.environment
        == "testing"
    )

    assert (
        snapshot.request_id
        == context.request_id
    )

    assert (
        snapshot.correlation_id
        == context.correlation_id
    )

    assert (
        snapshot.trace_id
        == context.trace_id
    )


def test_platform_service_lifecycle():

    platform = create_platform()

    service = object()

    platform.register_service(
        "test_service",
        service,
    )

    assert (
        platform.service(
            "test_service"
        )
        is service
    )


def test_platform_metrics_lifecycle():

    platform = create_platform()

    context = (
        platform.create_request_context(
            module_name="finance"
        )
    )

    platform.increment_metric(
        "operations_total",
        context=context,
    )

    metric = (
        platform.metrics.registry.get(
            "operations_total",
            labels={
                "module_name": "finance",
            },
        )
    )

    assert (
        metric.value
        == 1
    )


def test_platform_metric_timer():

    platform = create_platform()

    context = (
        platform.create_request_context(
            module_name="finance",
            operation="test",
        )
    )

    with platform.metric_timer(
        "operation_duration",
        context=context,
    ):

        total = sum(
            range(100)
        )

    assert (
        total
        == 4950
    )

    metric = (
        platform.metrics.registry.get(
            "operation_duration",
            labels={
                "module_name": "finance",
            },
        )
    )

    assert (
        metric.value
        >= 0
    )


def test_platform_governance():

    governance = (
        PlatformGovernance()
    )

    governance.register(
        PlatformComponent(
            name="platform.infrastructure",
            component_type="INFRASTRUCTURE",
            version="1.0.0",
        )
    )

    governance.register(
        PlatformComponent(
            name="platform.metrics",
            component_type="METRICS",
            version="1.0.0",
        )
    )

    governance.register(
        PlatformComponent(
            name="platform.diagnostics",
            component_type="DIAGNOSTICS",
            version="1.0.0",
        )
    )

    assert (
        governance.count()
        == 3
    )

    assert (
        governance.validate()
        is True
    )


def test_platform_infrastructure_repr():

    platform = create_platform()

    representation = repr(
        platform
    )

    assert (
        "PlatformInfrastructure"
        in representation
    )

    assert (
        "testing"
        in representation
    )


def test_final_platform_health_check():

    platform = create_platform()

    assert (
        platform.is_healthy()
        is True
    )
