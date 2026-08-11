"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.10.3

Command dispatcher event integration tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionContext,
    ExecutionResult,
    ExecutionTransactionBoundary,
)

from app.core.execution.events import (
    ExecutionEventType,
)

from app.core.execution.event_emitter import (
    RecordingExecutionEventEmitter,
)

@pytest.fixture(autouse=True)
def cleanup_command_registry():
    """
    Ensure the shared command registry is isolated
    between tests.
    """

    from app.core.execution import command_registry

    command_name = DispatcherEventCommand.command_name

    if command_registry.exists(command_name):
        command_registry.unregister(command_name)

    yield

    if command_registry.exists(command_name):
        command_registry.unregister(command_name)



class DispatcherEventCommand(BaseCommand):
    """
    Test command used for dispatcher event tests.
    """

    command_name = "test.dispatcher.events"
    permission_code = "test.dispatcher.events"

    def execute_name(self) -> str:
        """
        Return the operation represented by this command.
        """

        return self.command_name


class SuccessfulEventHandler(BaseCommandHandler):
    """
    Handler returning a successful execution result.
    """

    command_type = DispatcherEventCommand

    def handle(self, command, context):
        return ExecutionResult.success_result(
            data={"executed": True},
            message="Execution completed.",
        )


class FailedEventHandler(BaseCommandHandler):
    """
    Handler returning a failed execution result.
    """

    command_type = DispatcherEventCommand

    def handle(self, command, context):
        return ExecutionResult.failure_result(
            message="Execution failed.",
            error_code="TEST_FAILURE",
        )


class ExceptionEventHandler(BaseCommandHandler):
    """
    Handler raising an exception during execution.
    """

    command_type = DispatcherEventCommand

    def handle(self, command, context):
        raise RuntimeError(
            "handler execution failed"
        )


class RecordingTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Test transaction boundary that records lifecycle events.
    """

    def __init__(self):
        self.events = []

    def begin(self):
        self.events.append("begin")

    def commit(self):
        self.events.append("commit")

    def rollback(self):
        self.events.append("rollback")


def build_context():
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="events",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
    )


def build_dispatcher(
    handler,
    emitter=None,
    transaction_boundary=None,
):
    """
    Build a dispatcher configured for event testing.
    """

    dispatcher = CommandDispatcher(
        transaction_boundary=transaction_boundary,
        event_emitter=emitter,
    )

    dispatcher.registry.register(
        DispatcherEventCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_dispatcher_emits_started_and_completed_events():
    """
    Successful dispatch emits STARTED and COMPLETED
    execution events.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulEventHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        DispatcherEventCommand(),
        build_context(),
    )

    assert result.is_success()

    assert len(emitter.events) == 2

    assert (
        emitter.events[0].event_type
        is ExecutionEventType.STARTED
    )

    assert (
        emitter.events[1].event_type
        is ExecutionEventType.COMPLETED
    )

    assert (
        emitter.events[0].command_name
        == "test.dispatcher.events"
    )

    assert (
        emitter.events[1].command_name
        == "test.dispatcher.events"
    )


def test_dispatcher_emits_failed_event_for_failed_result():
    """
    A failed execution result emits STARTED followed
    by FAILED.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        FailedEventHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        DispatcherEventCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert len(emitter.events) == 2

    assert (
        emitter.events[0].event_type
        is ExecutionEventType.STARTED
    )

    assert (
        emitter.events[1].event_type
        is ExecutionEventType.FAILED
    )


def test_dispatcher_emits_failed_event_for_handler_exception():
    """
    A handler exception emits STARTED followed by
    FAILED while preserving the original exception.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        ExceptionEventHandler(),
        emitter=emitter,
    )

    with pytest.raises(
        RuntimeError,
        match="handler execution failed",
    ):
        dispatcher.dispatch(
            DispatcherEventCommand(),
            build_context(),
        )

    assert len(emitter.events) == 2

    assert (
        emitter.events[0].event_type
        is ExecutionEventType.STARTED
    )

    assert (
        emitter.events[1].event_type
        is ExecutionEventType.FAILED
    )


def test_dispatcher_does_not_emit_events_when_no_emitter_is_configured():
    """
    Dispatcher remains backward compatible when no
    event emitter is configured.
    """

    dispatcher = build_dispatcher(
        SuccessfulEventHandler()
    )

    result = dispatcher.dispatch(
        DispatcherEventCommand(),
        build_context(),
    )

    assert result.is_success()


def test_dispatcher_event_contains_execution_context():
    """
    Dispatcher-generated events preserve the execution
    context supplied to dispatch().
    """

    emitter = RecordingExecutionEventEmitter()

    context = build_context()

    dispatcher = build_dispatcher(
        SuccessfulEventHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        DispatcherEventCommand(),
        context,
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.context is context


def test_dispatcher_event_metadata_identifies_dispatcher():
    """
    Dispatcher-generated events identify the dispatcher
    as their event source.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulEventHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        DispatcherEventCommand(),
        build_context(),
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.metadata["source"] == "dispatcher"


def test_dispatcher_event_order_is_preserved_with_transaction():
    """
    Transaction-aware dispatch preserves event ordering
    around successful execution.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulEventHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        DispatcherEventCommand(),
        build_context(),
    )

    assert result.is_success()

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.COMPLETED,
    ]

    assert transaction.events == [
        "begin",
        "commit",
    ]
