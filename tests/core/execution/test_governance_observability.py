"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.7

Governance and observability integration tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionAuthorizer,
    ExecutionContext,
    ExecutionResult,
)

from app.core.execution.event_emitter import (
    ExecutionEventEmitter,
    RecordingExecutionEventEmitter,
)

from app.core.execution.events import (
    ExecutionEventType,
)


class ObservabilityTestCommand(BaseCommand):
    """
    Test command used for governance observability tests.
    """

    command_name = "test.governance.observability"

    permission_code = "test.governance.observability"

    def execute_name(self) -> str:
        """
        Return the operation represented by this command.
        """

        return self.command_name


class SuccessfulObservabilityHandler(
    BaseCommandHandler
):
    """
    Handler returning a successful execution result.
    """

    command_type = ObservabilityTestCommand

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


class FailedObservabilityHandler(
    BaseCommandHandler
):
    """
    Handler returning a failed execution result.
    """

    command_type = ObservabilityTestCommand

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.failure_result(
            message="Execution failed.",
            error_code="OBSERVABILITY_FAILURE",
        )


class ExceptionObservabilityHandler(
    BaseCommandHandler
):
    """
    Handler raising an exception during execution.
    """

    command_type = ObservabilityTestCommand

    def handle(
        self,
        command,
        context,
    ):
        raise RuntimeError(
            "observability handler failed"
        )


class DenyingObservabilityAuthorizer(
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
            reason="Permission denied.",
            metadata={
                "authorization_source": (
                    "observability-test"
                ),
            },
        )

        return _DenyingAuthorizer().authorize(
            command,
            context,
        )


class FailingExecutionEventEmitter(
    ExecutionEventEmitter
):
    """
    Event emitter that deliberately fails.

    Dispatcher observability failures must not
    alter command execution semantics.
    """

    def __init__(self):
        self.attempts = 0

    def emit(self, event):
        self.attempts += 1

        raise RuntimeError(
            "observability emitter failed"
        )


@pytest.fixture(autouse=True)
def cleanup_command_registry():
    """
    Ensure the shared command registry is isolated
    between tests.
    """

    from app.core.execution import command_registry

    command_name = (
        ObservabilityTestCommand.command_name
    )

    if command_registry.exists(command_name):
        command_registry.unregister(command_name)

    yield

    if command_registry.exists(command_name):
        command_registry.unregister(command_name)


def build_context() -> ExecutionContext:
    """
    Build a valid execution context containing
    observability correlation information.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="observability",
        request_id="request-observability-001",
        correlation_id="correlation-observability-001",
        trace_id="trace-observability-001",
        environment="testing",
        metadata={
            "governance_test": True,
        },
    )


def build_dispatcher(
    handler,
    *,
    emitter=None,
    authorizer=None,
):
    """
    Build a dispatcher configured for observability tests.
    """

    dispatcher = CommandDispatcher(
        authorizer=authorizer,
        event_emitter=emitter,
    )

    dispatcher.registry.register(
        ObservabilityTestCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_successful_governed_execution_emits_started_and_completed():
    """
    Successful execution emits STARTED followed by
    COMPLETED.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        ObservabilityTestCommand(),
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


def test_failed_result_emits_started_and_failed():
    """
    A failed execution result emits STARTED followed
    by FAILED.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        FailedObservabilityHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        ObservabilityTestCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert result.error_code == (
        "OBSERVABILITY_FAILURE"
    )

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
    ]


def test_handler_exception_emits_started_and_failed():
    """
    A handler exception emits STARTED followed by
    FAILED while preserving the original exception.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        ExceptionObservabilityHandler(),
        emitter=emitter,
    )

    with pytest.raises(
        RuntimeError,
        match="observability handler failed",
    ):
        dispatcher.dispatch(
            ObservabilityTestCommand(),
            build_context(),
        )

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.FAILED,
    ]


def test_authorization_denial_emits_started_and_denied():
    """
    Authorization denial is represented through the
    dispatcher observability lifecycle.

    The denial must produce STARTED followed by
    DENIED without executing the handler.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
        authorizer=DenyingObservabilityAuthorizer(),
    )

    with pytest.raises(
        Exception,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            ObservabilityTestCommand(),
            build_context(),
        )

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.DENIED,
    ]


def test_observability_event_preserves_execution_context():
    """
    Dispatcher-generated observability events preserve
    the exact execution context supplied by the caller.
    """

    emitter = RecordingExecutionEventEmitter()

    context = build_context()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        ObservabilityTestCommand(),
        context,
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.context is context


def test_observability_event_preserves_correlation_information():
    """
    Dispatcher-generated events preserve request,
    correlation, and trace identifiers.
    """

    emitter = RecordingExecutionEventEmitter()

    context = build_context()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        ObservabilityTestCommand(),
        context,
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.context.request_id == (
            "request-observability-001"
        )

        assert event.context.correlation_id == (
            "correlation-observability-001"
        )

        assert event.context.trace_id == (
            "trace-observability-001"
        )


def test_observability_event_identifies_dispatcher_source():
    """
    Dispatcher-generated events identify the dispatcher
    as their observability source.
    """

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        ObservabilityTestCommand(),
        build_context(),
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.metadata["source"] == (
            "dispatcher"
        )


def test_observability_event_preserves_context_metadata():
    """
    Execution context metadata remains available to
    dispatcher-generated observability events.
    """

    emitter = RecordingExecutionEventEmitter()

    context = build_context()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        ObservabilityTestCommand(),
        context,
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.context.metadata[
            "governance_test"
        ] is True


def test_event_emitter_failure_does_not_change_execution():
    """
    Observability infrastructure failure must not
    alter successful command execution semantics.
    """

    emitter = FailingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        SuccessfulObservabilityHandler(),
        emitter=emitter,
    )

    result = dispatcher.dispatch(
        ObservabilityTestCommand(),
        build_context(),
    )

    assert result.is_success()

    assert emitter.attempts == 2


def test_event_emitter_failure_does_not_mask_handler_exception():
    """
    Observability failure must not mask the original
    handler exception.
    """

    emitter = FailingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        ExceptionObservabilityHandler(),
        emitter=emitter,
    )

    with pytest.raises(
        RuntimeError,
        match="observability handler failed",
    ):
        dispatcher.dispatch(
            ObservabilityTestCommand(),
            build_context(),
        )

    assert emitter.attempts == 2
