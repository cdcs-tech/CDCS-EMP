"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Platform metrics and telemetry tests.
"""

from app.core.platform import (
    MetricsRegistry,
    PlatformConfig,
    PlatformMetrics,
    RequestContext,
    RuntimeContext,
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
        module_name="finance",
    )


def test_metric_registration():

    registry = MetricsRegistry()

    metric = registry.register(
        "operations_total"
    )

    assert (
        metric.name
        == "operations_total"
    )

    assert (
        metric.value
        == 0.0
    )

    assert (
        registry.count()
        == 1
    )


def test_metric_increment():

    registry = MetricsRegistry()

    registry.increment(
        "operations_total"
    )

    registry.increment(
        "operations_total",
        2,
    )

    assert (
        registry.value(
            "operations_total"
        )
        == 3
    )


def test_metric_set():

    registry = MetricsRegistry()

    registry.set(
        "active_users",
        15,
    )

    assert (
        registry.value(
            "active_users"
        )
        == 15
    )


def test_metric_labels():

    registry = MetricsRegistry()

    registry.increment(
        "operations_total",
        labels={
            "module": "finance",
        },
    )

    metric = registry.get(
        "operations_total",
        labels={
            "module": "finance",
        },
    )

    assert (
        metric.labels["module"]
        == "finance"
    )

    assert (
        metric.value
        == 1
    )


def test_metric_listing():

    registry = MetricsRegistry()

    registry.register(
        "metric_a"
    )

    registry.register(
        "metric_b"
    )

    assert (
        registry.count()
        == 2
    )

    assert len(
        registry.all()
    ) == 2


def test_metric_clear():

    registry = MetricsRegistry()

    registry.register(
        "metric_a"
    )

    registry.clear()

    assert (
        registry.count()
        == 0
    )


def test_platform_metrics_increment():

    metrics = PlatformMetrics()

    context = create_context()

    metrics.increment(
        "operations_total",
        context=context,
    )

    metric = metrics.registry.get(
        "operations_total",
        labels={
            "module_name": "finance",
        },
    )

    assert (
        metric.value
        == 1
    )


def test_platform_metrics_custom_labels():

    metrics = PlatformMetrics()

    metrics.increment(
        "events_total",
        event_type="TEST_EVENT",
    )

    metric = metrics.registry.get(
        "events_total",
        labels={
            "event_type": "TEST_EVENT",
        },
    )

    assert (
        metric.value
        == 1
    )


def test_platform_metrics_set():

    metrics = PlatformMetrics()

    metrics.set(
        "active_connections",
        10,
    )

    assert (
        metrics.registry.value(
            "active_connections"
        )
        == 10
    )


def test_metric_timer():

    metrics = PlatformMetrics()

    with metrics.timer(
        "operation_duration"
    ) as timer:

        total = sum(
            range(100)
        )

    assert total == 4950

    assert (
        timer.elapsed is not None
    )

    assert (
        timer.elapsed >= 0
    )

    assert (
        metrics.registry.value(
            "operation_duration"
        )
        >= 0
    )


def test_metric_timer_with_context():

    metrics = PlatformMetrics()

    context = create_context()

    with metrics.timer(
        "operation_duration",
        context=context,
    ):

        pass

    metric = metrics.registry.get(
        "operation_duration",
        labels={
            "module_name": "finance",
        },
    )

    assert (
        metric.value >= 0
    )


def test_metrics_repr():

    metrics = PlatformMetrics()

    representation = repr(
        metrics
    )

    assert (
        "PlatformMetrics"
        in representation
    )
