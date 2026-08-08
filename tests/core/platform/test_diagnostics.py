"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Runtime diagnostics tests.
"""

from app.core.platform import (
    DiagnosticSnapshot,
    DiagnosticStatus,
    PlatformConfig,
    PlatformMetrics,
    PlatformServiceContainer,
    RequestContext,
    RuntimeContext,
    RuntimeDiagnostics,
)


def create_context():

    runtime = RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )

    return RequestContext(
        runtime=runtime,
        user_id="user-001",
        module_name="platform",
        operation="diagnostics",
    )


def test_diagnostic_status_values():

    assert (
        DiagnosticStatus.HEALTHY
        == "HEALTHY"
    )

    assert (
        DiagnosticStatus.WARNING
        == "WARNING"
    )

    assert (
        DiagnosticStatus.UNHEALTHY
        == "UNHEALTHY"
    )


def test_diagnostic_snapshot_creation():

    snapshot = DiagnosticSnapshot(
        status=DiagnosticStatus.HEALTHY,
        environment="testing",
        application_name="CDCS-EMP",
        application_version="1.0.0",
        service_count=2,
        metric_count=3,
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
        snapshot.service_count
        == 2
    )

    assert (
        snapshot.metric_count
        == 3
    )


def test_diagnostic_snapshot_health():

    snapshot = DiagnosticSnapshot(
        status=DiagnosticStatus.HEALTHY,
        environment="testing",
        application_name="CDCS-EMP",
        application_version="1.0.0",
        service_count=0,
        metric_count=0,
    )

    assert (
        snapshot.is_healthy()
        is True
    )


def test_diagnostic_snapshot_to_dict():

    snapshot = DiagnosticSnapshot(
        status=DiagnosticStatus.HEALTHY,
        environment="testing",
        application_name="CDCS-EMP",
        application_version="1.0.0",
        service_count=1,
        metric_count=2,
        details={
            "runtime_valid": True,
        },
    )

    data = snapshot.to_dict()

    assert (
        data["status"]
        == DiagnosticStatus.HEALTHY
    )

    assert (
        data["environment"]
        == "testing"
    )

    assert (
        data["service_count"]
        == 1
    )

    assert (
        data["metric_count"]
        == 2
    )

    assert (
        data["details"]["runtime_valid"]
        is True
    )


def test_runtime_diagnostics_check():

    services = (
        PlatformServiceContainer()
    )

    metrics = PlatformMetrics()

    services.register(
        "test_service",
        object(),
    )

    metrics.increment(
        "test_metric"
    )

    diagnostics = RuntimeDiagnostics(
        service_container=services,
        metrics=metrics,
    )

    context = create_context()

    snapshot = diagnostics.check(
        context
    )

    assert (
        snapshot.status
        == DiagnosticStatus.HEALTHY
    )

    assert (
        snapshot.service_count
        == 1
    )

    assert (
        snapshot.metric_count
        == 1
    )


def test_runtime_diagnostics_context_identity():

    diagnostics = RuntimeDiagnostics()

    context = create_context()

    snapshot = diagnostics.check(
        context
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


def test_runtime_diagnostics_status():

    diagnostics = RuntimeDiagnostics()

    context = create_context()

    assert (
        diagnostics.status(
            context
        )
        == DiagnosticStatus.HEALTHY
    )


def test_runtime_diagnostics_is_healthy():

    diagnostics = RuntimeDiagnostics()

    context = create_context()

    assert (
        diagnostics.is_healthy(
            context
        )
        is True
    )


def test_runtime_diagnostics_repr():

    diagnostics = RuntimeDiagnostics()

    assert (
        "RuntimeDiagnostics"
        in repr(diagnostics)
    )
