"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.10.3

Execution event integration with observability tests.
"""

import logging

import pytest

from app.core.execution import (
    ExecutionContext,
)

from app.core.execution.events import (
    ExecutionEvent,
    ExecutionEventType,
)

from app.core.platform.execution_observability import (
    PlatformExecutionObserver,
)

from app.core.platform.logging import (
    PlatformLogger,
)

from app.core.platform.metrics import (
    MetricsRegistry,
    PlatformMetrics,
)


class RecordingHandler(
    logging.Handler
):
    """
    Logging handler used to capture
    structured platform log records.
    """

    def __init__(self):
        super().__init__()

        self.records = []

    def emit(
        self,
        record,
    ):
        self.records.append(record)


def build_context():
    """
    Build a valid execution context for
    observability tests.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="execution",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
    )


def build_event(
    event_type=ExecutionEventType.STARTED,
    outcome="success",
):
    """
    Build a valid execution event.
    """

    return ExecutionEvent(
        event_type=event_type,
        command_name="test.command",
        context=build_context(),
        outcome=outcome,
    )


def build_observer():
    """
    Build an observer with isolated
    test infrastructure.
    """

    logger = logging.getLogger(
        "cdcs_emp.test_execution_observability"
    )

    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    handler = RecordingHandler()

    logger.addHandler(
        handler
    )

    platform_logger = PlatformLogger(
        logger=logger
    )

    metrics = PlatformMetrics(
        registry=MetricsRegistry()
    )

    observer = PlatformExecutionObserver(
        logger=platform_logger,
        metrics=metrics,
    )

    return (
        observer,
        handler,
        metrics,
    )


def test_observer_accepts_execution_event():
    """
    The observer accepts a valid execution event.
    """

    observer, _, _ = build_observer()

    observer.emit(
        build_event()
    )


def test_observer_rejects_invalid_event():
    """
    The observer requires an ExecutionEvent.
    """

    observer, _, _ = build_observer()

    with pytest.raises(
        TypeError,
        match="event",
    ):
        observer.emit(
            object()
        )


@pytest.mark.parametrize(
    (
        "event_type",
        "outcome",
        "metric_name",
        "log_level",
    ),
    [
        (
            ExecutionEventType.STARTED,
            "success",
            "execution.events.started",
            logging.INFO,
        ),
        (
            ExecutionEventType.COMPLETED,
            "success",
            "execution.events.completed",
            logging.INFO,
        ),
        (
            ExecutionEventType.FAILED,
            "failure",
            "execution.events.failed",
            logging.ERROR,
        ),
        (
            ExecutionEventType.DENIED,
            "denied",
            "execution.events.denied",
            logging.WARNING,
        ),
    ],
)
def test_observer_maps_execution_events_to_observability(
    event_type,
    outcome,
    metric_name,
    log_level,
):
    """
    Each execution lifecycle event produces
    the corresponding log and metric signal.
    """

    observer, handler, metrics = (
        build_observer()
    )

    event = build_event(
        event_type=event_type,
        outcome=outcome,
    )

    observer.emit(
        event
    )

    assert len(
        handler.records
    ) == 1

    record = handler.records[0]

    assert record.levelno == log_level

    assert (
        record.command_name
        == "test.command"
    )

    assert (
        record.event_type
        == event_type.value
    )

    assert (
        record.outcome
        == outcome
    )

    assert metrics.registry.value(
        metric_name,
        labels={
            "command_name": "test.command",
            "event_type": event_type.value,
            "outcome": outcome,
            "module_name": "test",
        },
    ) == 1.0


def test_observer_propagates_execution_context_to_logging():
    """
    Execution context identifiers are preserved
    in structured logging metadata.
    """

    observer, handler, _ = (
        build_observer()
    )

    observer.emit(
        build_event()
    )

    record = handler.records[0]

    assert (
        record.request_id
        == "request-001"
    )

    assert (
        record.correlation_id
        == "correlation-001"
    )

    assert (
        record.trace_id
        == "trace-001"
    )

    assert (
        record.user_id
        == "user-001"
    )

    assert (
        record.module_name
        == "test"
    )

    assert (
        record.operation
        == "execution"
    )


def test_observer_isolates_logging_failure():
    """
    Logging failures do not prevent metric emission.
    """

    class FailingLogger:
        def info(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "logging failure"
            )

        def warning(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "logging failure"
            )

        def error(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "logging failure"
            )

    metrics = PlatformMetrics(
        registry=MetricsRegistry()
    )

    observer = PlatformExecutionObserver(
        logger=FailingLogger(),
        metrics=metrics,
    )

    observer.emit(
        build_event(
            ExecutionEventType.COMPLETED
        )
    )

    assert metrics.registry.value(
        "execution.events.completed",
        labels={
            "command_name": "test.command",
            "event_type": (
                ExecutionEventType.COMPLETED.value
            ),
            "outcome": "success",
            "module_name": "test",
        },
    ) == 1.0


def test_observer_isolates_metric_failure():
    """
    Metric failures do not prevent logging.
    """

    observer, handler, _ = (
        build_observer()
    )

    class FailingMetrics:
        def increment(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "metric failure"
            )

    observer.metrics = FailingMetrics()

    observer.emit(
        build_event(
            ExecutionEventType.COMPLETED
        )
    )

    assert len(
        handler.records
    ) == 1

    record = handler.records[0]

    assert (
        record.command_name
        == "test.command"
    )

    assert (
        record.event_type
        == ExecutionEventType.COMPLETED.value
    )

    assert (
        record.outcome
        == "success"
    )
