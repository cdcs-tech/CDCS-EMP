"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Integrated platform infrastructure tests.
"""

from app.core.platform import (
    PlatformConfig,
    PlatformInfrastructure,
    PlatformLogger,
    PlatformMetrics,
    PlatformServiceContainer,
    RequestContext,
    RuntimeContext,
    RuntimeDiagnostics,
)


def create_runtime():

    return RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )


def create_infrastructure():

    runtime = create_runtime()

    services = (
        PlatformServiceContainer()
    )

    logger = PlatformLogger(
        "test_infrastructure"
    )

    metrics = PlatformMetrics()

    diagnostics = RuntimeDiagnostics(
        service_container=services,
        metrics=metrics,
    )

    return PlatformInfrastructure(
        runtime=runtime,
        services=services,
        logger=logger,
        metrics=metrics,
        diagnostics=diagnostics,
    )


def test_infrastructure_creation():

    infrastructure = (
        create_infrastructure()
    )

    assert (
        infrastructure.runtime
        is not None
    )

    assert (
        infrastructure.services
        is not None
    )

    assert (
        infrastructure.logger
        is not None
    )

    assert (
        infrastructure.metrics
        is not None
    )

    assert (
        infrastructure.diagnostics
        is not None
    )


def test_create_request_context():

    infrastructure = (
        create_infrastructure()
    )

    context = (
        infrastructure.create_request_context(
            user_id="user-001",
            module_name="platform",
            operation="test",
        )
    )

    assert isinstance(
        context,
        RequestContext,
    )

    assert (
        context.user_id
        == "user-001"
    )

    assert (
        context.module_name
        == "platform"
    )

    assert (
        context.operation
        == "test"
    )

    assert (
        context.environment
        == "testing"
    )


def test_health_check():

    infrastructure = (
        create_infrastructure()
    )

    context = (
        infrastructure.create_request_context()
    )

    snapshot = (
        infrastructure.health_check(
            context
        )
    )

    assert snapshot.is_healthy()

    assert (
        snapshot.environment
        == "testing"
    )


def test_default_health_check():

    infrastructure = (
        create_infrastructure()
    )

    snapshot = (
        infrastructure.health_check()
    )

    assert snapshot.is_healthy()


def test_is_healthy():

    infrastructure = (
        create_infrastructure()
    )

    assert (
        infrastructure.is_healthy()
        is True
    )


def test_service_registration_and_resolution():

    infrastructure = (
        create_infrastructure()
    )

    service = object()

    infrastructure.register_service(
        "test_service",
        service,
    )

    assert (
        infrastructure.service(
            "test_service"
        )
        is service
    )


def test_service_replacement():

    infrastructure = (
        create_infrastructure()
    )

    first = object()
    second = object()

    infrastructure.register_service(
        "test_service",
        first,
    )

    infrastructure.register_service(
        "test_service",
        second,
        replace=True,
    )

    assert (
        infrastructure.service(
            "test_service"
        )
        is second
    )


def test_increment_metric():

    infrastructure = (
        create_infrastructure()
    )

    context = (
        infrastructure.create_request_context(
            module_name="finance"
        )
    )

    infrastructure.increment_metric(
        "operations_total",
        context=context,
    )

    metric = (
        infrastructure.metrics.registry.get(
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


def test_metric_timer():

    infrastructure = (
        create_infrastructure()
    )

    context = (
        infrastructure.create_request_context(
            module_name="finance"
        )
    )

    with infrastructure.metric_timer(
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
        infrastructure.metrics.registry.get(
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


def test_log_context():

    infrastructure = (
        create_infrastructure()
    )

    context = (
        infrastructure.create_request_context(
            module_name="platform",
            operation="test",
        )
    )

    infrastructure.log_context(
        "Platform test message",
        context,
    )


def test_log_context_invalid_level():

    infrastructure = (
        create_infrastructure()
    )

    context = (
        infrastructure.create_request_context()
    )

    try:

        infrastructure.log_context(
            "Invalid level",
            context,
            level="invalid",
        )

        assert False

    except ValueError as exc:

        assert (
            "Unsupported log level"
            in str(exc)
        )


def test_infrastructure_repr():

    infrastructure = (
        create_infrastructure()
    )

    representation = repr(
        infrastructure
    )

    assert (
        "PlatformInfrastructure"
        in representation
    )

    assert (
        "testing"
        in representation
    )
