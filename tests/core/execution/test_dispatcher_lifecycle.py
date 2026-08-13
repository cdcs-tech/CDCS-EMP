"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.3

Dispatcher lifecycle governance integration tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionAuthorizer,
    ExecutionContext,
    ExecutionContractException,
    ExecutionResult,
)

from app.core.execution.events import (
    ExecutionEventType,
)

from app.core.execution.event_emitter import (
    RecordingExecutionEventEmitter,
)

from app.core.execution.transaction import (
    ExecutionTransactionBoundary,
)


class LifecycleTestCommand(BaseCommand):
    """
    Test command used for dispatcher lifecycle tests.
    """

    command_name = "test.dispatcher.lifecycle"

    permission_code = "test.dispatcher.lifecycle"

    def execute_name(self) -> str:
        """
        Return the operation represented by this command.
        """

        return self.command_name


class SuccessfulLifecycleHandler(BaseCommandHandler):
    """
    Handler returning a successful execution result.
    """

    command_type = LifecycleTestCommand

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.success_result(
            data={
                "executed": True,
            },
            message="Execution completed.",
        )


class FailedLifecycleHandler(BaseCommandHandler):
    """
    Handler returning a failed execution result.
    """

    command_type = LifecycleTestCommand

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.failure_result(
            message="Execution failed.",
            error_code="TEST_FAILURE",
        )


class ExceptionLifecycleHandler(BaseCommandHandler):
    """
    Handler raising an exception during execution.
    """

    command_type = LifecycleTestCommand

    def handle(
        self,
        command,
        context,
    ):
        raise RuntimeError(
            "lifecycle handler failed"
        )


class DenyingLifecycleAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that denies command execution.
    """

    def authorize(
        self,
        command,
        context,
    ):
        from app.core.execution.authorization import (
            AuthorizationDecision,
        )

        return AuthorizationDecision.deny(
            reason="Permission denied."
        )


class RecordingTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Transaction boundary that records
    lifecycle operations.
    """

    def __init__(self):
        self.events = []

    def begin(self) -> None:
        self.events.append("begin")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")


@pytest.fixture(autouse=True)
def cleanup_command_registry():
    """
    Ensure the shared command registry is isolated
    between tests.
    """

    from app.core.execution import command_registry

    command_name = LifecycleTestCommand.command_name

    if command_registry.exists(command_name):
        command_registry.unregister(command_name)

    yield

    if command_registry.exists(command_name):
        command_registry.unregister(command_name)


def build_context() -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="lifecycle",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={},
    )


def build_dispatcher(
    handler,
    *,
    emitter=None,
    transaction_boundary=None,
    authorizer=None,
):
    """
    Build a dispatcher configured for lifecycle tests.
    """

    dispatcher = CommandDispatcher(
        authorizer=authorizer,
        transaction_boundary=transaction_boundary,
        event_emitter=emitter,
    )

    dispatcher.registry.register(
        LifecycleTestCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_successful_dispatch_reaches_completed_lifecycle():
    """
    A successful command execution reaches the
    COMPLETED lifecycle state.

    The externally observable governance sequence
    is STARTED followed by COMPLETED.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulLifecycleHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        LifecycleTestCommand(),
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


def test_failed_result_reaches_failed_lifecycle():
    """
    A failed execution result reaches the FAILED
    lifecycle state.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        FailedLifecycleHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        LifecycleTestCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert result.error_code == "TEST_FAILURE"

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
    ]


def test_handler_exception_reaches_failed_lifecycle():
    """
    A handler exception transitions execution to
    FAILED while preserving the original exception.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        ExceptionLifecycleHandler(),
        emitter=emitter,
    )

    with pytest.raises(
        RuntimeError,
        match="lifecycle handler failed",
    ):
        dispatcher.dispatch(
            LifecycleTestCommand(),
            build_context(),
        )

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
    ]


def test_authorization_denial_reaches_denied_lifecycle():
    """
    Authorization denial transitions execution to
    the DENIED lifecycle state and prevents handler
    execution.
    """

    emitter = RecordingExecutionEventEmitter()

    handler = SuccessfulLifecycleHandler()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        authorizer=DenyingLifecycleAuthorizer(),
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            LifecycleTestCommand(),
            build_context(),
        )

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.DENIED,
    ]


def test_authorization_denial_does_not_begin_transaction():
    """
    Authorization denial occurs before transaction
    execution begins.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulLifecycleHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
        authorizer=DenyingLifecycleAuthorizer(),
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            LifecycleTestCommand(),
            build_context(),
        )

    assert transaction.events == []

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.DENIED,
    ]


def test_successful_lifecycle_preserves_transaction_order():
    """
    Successful lifecycle execution preserves the
    transaction ordering:

        STARTED -> begin -> commit -> COMPLETED
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulLifecycleHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        LifecycleTestCommand(),
        build_context(),
    )

    assert result.is_success()

    assert transaction.events == [
        "begin",
        "commit",
    ]

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.COMPLETED,
    ]


def test_failed_result_preserves_transaction_order():
    """
    A failed execution result rolls back the
    transaction and reaches FAILED.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        FailedLifecycleHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        LifecycleTestCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert transaction.events == [
        "begin",
        "rollback",
    ]

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
    ]


def test_handler_exception_preserves_transaction_order():
    """
    A handler exception rolls back the transaction
    and reaches FAILED.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        ExceptionLifecycleHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    with pytest.raises(
        RuntimeError,
        match="lifecycle handler failed",
    ):
        dispatcher.dispatch(
            LifecycleTestCommand(),
            build_context(),
        )

    assert transaction.events == [
        "begin",
        "rollback",
    ]

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
    ]


def test_lifecycle_event_context_is_preserved():
    """
    Dispatcher lifecycle events preserve the exact
    execution context supplied to dispatch().
    """

    emitter = RecordingExecutionEventEmitter()

    context = build_context()

    dispatcher = build_dispatcher(
        SuccessfulLifecycleHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        LifecycleTestCommand(),
        context,
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.context is context


def test_lifecycle_event_source_is_dispatcher():
    """
    Dispatcher lifecycle events identify the
    dispatcher as their source.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulLifecycleHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        LifecycleTestCommand(),
        build_context(),
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.metadata["source"] == "dispatcher"
