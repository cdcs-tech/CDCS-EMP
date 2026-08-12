"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.10.4

Observability execution event emitter tests.
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

from app.core.execution.observability_emitter import (
    ObservabilityExecutionEventEmitter,
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
        self.records.append(
            record
        )


def build_context():
    """
    Build a valid execution context
    for emitter tests.
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
    metadata=None,
):
    """
    Build a valid execution event.
    """

    return ExecutionEvent(
        event_type=event_type,
        command_name="test.command",
        context=build_context(),
        outcome=outcome,
        metadata=metadata or {},
    )


def build_emitter():
    """
    Build an emitter with isolated
    test infrastructure.
    """

    logger = logging.getLogger(
        "cdcs_emp.test_execution_observability_emitter"
    )

    logger.handlers.clear()
    logger.setLevel(
        logging.DEBUG
    )

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

    emitter = (
        ObservabilityExecutionEventEmitter(
            logger=platform_logger,
            metrics=metrics,
        )
    )

    return (
        emitter,
        handler,
        metrics,
    )


def test_emitter_accepts_execution_event():
    """
    The emitter accepts a valid execution event.
    """

    emitter, _, _ = build_emitter()

    emitter.emit(
        build_event()
    )


def test_emitter_rejects_invalid_event():
    """
    The emitter requires an ExecutionEvent.
    """

    emitter, _, _ = build_emitter()

    with pytest.raises(
        TypeError,
        match="event",
    ):
        emitter.emit(
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
            "execution.started",
            logging.INFO,
        ),
        (
            ExecutionEventType.COMPLETED,
            "success",
            "execution.completed",
            logging.INFO,
        ),
        (
            ExecutionEventType.FAILED,
            "failure",
            "execution.failed",
            logging.ERROR,
        ),
        (
            ExecutionEventType.DENIED,
            "denied",
            "execution.denied",
            logging.WARNING,
        ),
    ],
)
def test_emitter_maps_execution_events_to_observability(
    event_type,
    outcome,
    metric_name,
    log_level,
):
    """
    Each execution lifecycle event produces
    the corresponding log and metric signal.
    """

    emitter, handler, metrics = (
        build_emitter()
    )

    emitter.emit(
        build_event(
            event_type=event_type,
            outcome=outcome,
        )
    )

    assert len(
        handler.records
    ) == 1

    record = handler.records[0]

    assert (
        record.levelno
        == log_level
    )

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


def test_emitter_propagates_execution_context_to_logging():
    """
    Execution context identifiers are preserved
    in structured logging metadata.
    """

    emitter, handler, _ = (
        build_emitter()
    )

    emitter.emit(
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


def test_emitter_propagates_event_metadata_to_logging():
    """
    Event metadata is preserved in the
    structured logging record.
    """

    emitter, handler, _ = (
        build_emitter()
    )

    emitter.emit(
        build_event(
            event_type=(
                ExecutionEventType.FAILED
            ),
            outcome="failure",
            metadata={
                "source": "dispatcher",
                "error_code": "EXEC-001",
            },
        )
    )

    record = handler.records[0]

    assert (
        record.source
        == "dispatcher"
    )

    assert (
        record.error_code
        == "EXEC-001"
    )


def test_emitter_isolates_logging_failure():
    """
    Logging failures do not prevent
    metric emission.
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

    emitter = (
        ObservabilityExecutionEventEmitter(
            logger=FailingLogger(),
            metrics=metrics,
        )
    )

    emitter.emit(
        build_event(
            ExecutionEventType.COMPLETED
        )
    )

    assert metrics.registry.value(
        "execution.completed",
        labels={
            "command_name": "test.command",
            "event_type": (
                ExecutionEventType.COMPLETED.value
            ),
            "outcome": "success",
            "module_name": "test",
        },
    ) == 1.0


def test_emitter_isolates_metric_failure():
    """
    Metric failures do not prevent
    logging.
    """

    emitter, handler, _ = (
        build_emitter()
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

    emitter.metrics = (
        FailingMetrics()
    )

    emitter.emit(
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


def test_emitter_isolates_metric_and_logging_failures():
    """
    Simultaneous metric and logging failures
    do not propagate through the emitter.
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

    class FailingMetrics:
        def increment(
            self,
            *args,
            **kwargs,
        ):
            raise RuntimeError(
                "metric failure"
            )

    emitter = (
        ObservabilityExecutionEventEmitter(
            logger=FailingLogger(),
            metrics=FailingMetrics(),
        )
    )

    emitter.emit(
        build_event(
            ExecutionEventType.FAILED,
            outcome="failure",
        )
    )
