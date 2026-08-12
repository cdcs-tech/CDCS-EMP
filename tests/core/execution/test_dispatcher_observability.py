"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.10.5

Command dispatcher observability integration tests.
"""

import logging

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionContext,
    ExecutionResult,
)

from app.core.execution.event_emitter import (
    ExecutionEventEmitter,
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


class RecordingHandler(logging.Handler):
    """
    Logging handler used to capture
    structured platform log records.
    """

    def __init__(self):
        super().__init__()

        self.records = []

    def emit(self, record):
        self.records.append(record)


class DispatcherObservabilityCommand(
    BaseCommand
):
    """
    Test command used for dispatcher
    observability integration tests.
    """

    command_name = (
        "test.dispatcher.observability"
    )

    permission_code = (
        "test.dispatcher.observability"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented
        by this command.
        """

        return self.command_name


class SuccessfulHandler(
    BaseCommandHandler
):
    """
    Handler returning a successful result.
    """

    command_type = (
        DispatcherObservabilityCommand
    )

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.success_result(
            data={
                "executed": True
            },
            message="Execution completed.",
        )


class FailedHandler(
    BaseCommandHandler
):
    """
    Handler returning a failed result.
    """

    command_type = (
        DispatcherObservabilityCommand
    )

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.failure_result(
            message="Execution failed.",
            error_code="TEST_FAILURE",
        )


class ExceptionHandler(
    BaseCommandHandler
):
    """
    Handler raising an exception.
    """

    command_type = (
        DispatcherObservabilityCommand
    )

    def handle(
        self,
        command,
        context,
    ):
        raise RuntimeError(
            "handler execution failed"
        )


class FailingObservabilityEmitter(
    ExecutionEventEmitter
):
    """
    Emitter that raises an exception when
    observability is attempted.
    """

    def emit(
        self,
        event,
    ):
        raise RuntimeError(
            "observability failure"
        )


@pytest.fixture(autouse=True)
def cleanup_command_registry():
    """
    Ensure the shared command registry is
    isolated between tests.
    """

    from app.core.execution import (
        command_registry,
    )

    command_name = (
        DispatcherObservabilityCommand
        .command_name
    )

    if command_registry.exists(
        command_name
    ):
        command_registry.unregister(
            command_name
        )

    yield

    if command_registry.exists(
        command_name
    ):
        command_registry.unregister(
            command_name
        )


def build_context():
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="observability",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
    )


def build_observability_emitter():
    """
    Build an observability emitter with
    isolated logging and metrics infrastructure.
    """

    logger = logging.getLogger(
        "cdcs_emp.test_dispatcher_observability"
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


def build_dispatcher(
    handler,
    emitter=None,
):
    """
    Build a dispatcher configured for
    observability integration testing.
    """

    dispatcher = CommandDispatcher(
        event_emitter=emitter,
    )

    dispatcher.registry.register(
        DispatcherObservabilityCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_dispatcher_integrates_with_observability_emitter():
    """
    Dispatcher execution reaches the platform
    observability emitter.
    """

    (
        emitter,
        handler,
        metrics,
    ) = build_observability_emitter()

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        DispatcherObservabilityCommand(),
        build_context(),
    )

    assert result.is_success()

    assert len(handler.records) == 2

    assert [
        record.event_type
        for record in handler.records
    ] == [
        "execution.started",
        "execution.completed",
    ]

    assert metrics.registry.value(
        "execution.started",
        labels={
            "command_name": (
                "test.dispatcher.observability"
            ),
            "event_type": (
                "execution.started"
            ),
            "outcome": "success",
            "module_name": "test",
        },
    ) == 1.0

    assert metrics.registry.value(
        "execution.completed",
        labels={
            "command_name": (
                "test.dispatcher.observability"
            ),
            "event_type": (
                "execution.completed"
            ),
            "outcome": "success",
            "module_name": "test",
        },
    ) == 1.0


def test_dispatcher_observability_preserves_context():
    """
    Dispatcher execution context is propagated
    into platform observability logging.
    """

    (
        emitter,
        handler,
        _,
    ) = build_observability_emitter()

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        DispatcherObservabilityCommand(),
        build_context(),
    )

    assert len(handler.records) == 2

    for record in handler.records:
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
            == "observability"
        )


def test_dispatcher_observability_preserves_source_metadata():
    """
    Dispatcher-generated execution events retain
    their dispatcher source metadata in logging.
    """

    (
        emitter,
        handler,
        _,
    ) = build_observability_emitter()

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        DispatcherObservabilityCommand(),
        build_context(),
    )

    assert len(handler.records) == 2

    for record in handler.records:
        assert (
            record.source
            == "dispatcher"
        )


def test_dispatcher_failed_result_reaches_observability():
    """
    A failed execution result produces
    STARTED and FAILED observability signals.
    """

    (
        emitter,
        handler,
        metrics,
    ) = build_observability_emitter()

    dispatcher = build_dispatcher(
        FailedHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        DispatcherObservabilityCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert [
        record.event_type
        for record in handler.records
    ] == [
        "execution.started",
        "execution.failed",
    ]

    assert metrics.registry.value(
        "execution.failed",
        labels={
            "command_name": (
                "test.dispatcher.observability"
            ),
            "event_type": (
                "execution.failed"
            ),
            "outcome": "failure",
            "module_name": "test",
        },
    ) == 1.0

    assert (
        handler.records[1].error_code
        == "TEST_FAILURE"
    )


def test_dispatcher_exception_reaches_observability():
    """
    A handler exception produces STARTED and
    FAILED observability signals while the
    original exception is preserved.
    """

    (
        emitter,
        handler,
        metrics,
    ) = build_observability_emitter()

    dispatcher = build_dispatcher(
        ExceptionHandler(),
        emitter=emitter,
    )

    with pytest.raises(
        RuntimeError,
        match="handler execution failed",
    ):
        dispatcher.dispatch(
            DispatcherObservabilityCommand(),
            build_context(),
        )

    assert [
        record.event_type
        for record in handler.records
    ] == [
        "execution.started",
        "execution.failed",
    ]

    assert metrics.registry.value(
        "execution.failed",
        labels={
            "command_name": (
                "test.dispatcher.observability"
            ),
            "event_type": (
                "execution.failed"
            ),
            "outcome": "failure",
            "module_name": "test",
        },
    ) == 1.0


def test_dispatcher_isolates_observability_failure():
    """
    Observability emitter failures do not
    interfere with command execution.
    """

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        emitter=FailingObservabilityEmitter(),
    )

    result = dispatcher.dispatch(
        DispatcherObservabilityCommand(),
        build_context(),
    )

    assert result.is_success()


def test_dispatcher_accepts_observability_emitter():
    """
    Dispatcher accepts an observability emitter
    implementing the execution event contract.
    """

    (
        emitter,
        _,
        _,
    ) = build_observability_emitter()

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        emitter=emitter,
    )

    assert (
        dispatcher.event_emitter
        is emitter
    )
