"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.8

Execution governance regression tests.
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

from app.core.execution.authorization import (
    AuthorizationDecision,
)

from app.core.execution.authorization_service import (
    ExecutionAuthorizationService,
)

from app.core.execution.authorization_enforcement import (
    GovernanceAwareAuthorizationEnforcement,
)

from app.core.execution.events import (
    ExecutionEventType,
)

from app.core.execution.event_emitter import (
    RecordingExecutionEventEmitter,
)

from app.core.execution.governance import (
    ExecutionGovernance,
)

from app.core.execution.transaction import (
    ExecutionTransactionBoundary,
)


class GovernanceRegressionCommand(BaseCommand):
    """
    Command used for consolidated governance
    regression testing.
    """

    command_name = "test.governance.regression"

    permission_code = "test.governance.regression"

    def execute_name(self) -> str:
        """
        Return the operation represented by
        this command.
        """

        return self.command_name


class SuccessfulGovernanceHandler(
    BaseCommandHandler
):
    """
    Handler returning a successful result.
    """

    command_type = GovernanceRegressionCommand

    def __init__(self):
        self.called = False

    def handle(
        self,
        command,
        context,
    ):
        self.called = True

        return ExecutionResult.success_result(
            data={
                "executed": True,
            },
            message="Execution completed.",
        )


class FailedGovernanceHandler(
    BaseCommandHandler
):
    """
    Handler returning a failed result.
    """

    command_type = GovernanceRegressionCommand

    def __init__(self):
        self.called = False

    def handle(
        self,
        command,
        context,
    ):
        self.called = True

        return ExecutionResult.failure_result(
            message="Execution failed.",
            error_code="REGRESSION_FAILURE",
        )


class ExceptionGovernanceHandler(
    BaseCommandHandler
):
    """
    Handler raising an execution exception.
    """

    command_type = GovernanceRegressionCommand

    def __init__(self):
        self.called = False

    def handle(
        self,
        command,
        context,
    ):
        self.called = True

        raise RuntimeError(
            "governance regression failure"
        )


class DenyingGovernanceAuthorizer(
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
        return AuthorizationDecision.deny(
            reason="Permission denied.",
            metadata={
                "authorization_source": (
                    "governance-regression"
                ),
            },
        )


class AllowingGovernanceAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that explicitly allows execution.
    """

    def authorize(
        self,
        command,
        context,
    ):
        return AuthorizationDecision.allow(
            reason="Permission granted.",
            metadata={
                "authorization_source": (
                    "governance-regression"
                ),
            },
        )


class RecordingTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Transaction boundary recording lifecycle
    operations.
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
    Isolate the shared command registry between tests.
    """

    from app.core.execution import command_registry

    command_name = (
        GovernanceRegressionCommand.command_name
    )

    if command_registry.exists(command_name):
        command_registry.unregister(
            command_name
        )

    yield

    if command_registry.exists(command_name):
        command_registry.unregister(
            command_name
        )


def build_context() -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="governance-regression",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "regression": True,
        },
    )


def build_dispatcher(
    handler,
    *,
    emitter=None,
    transaction_boundary=None,
    authorizer=None,
    authorization_enforcement=None,
):
    """
    Build a dispatcher configured for governance
    regression testing.
    """

    dispatcher = CommandDispatcher(
        authorizer=authorizer,
        authorization_enforcement=(
            authorization_enforcement
        ),
        transaction_boundary=(
            transaction_boundary
        ),
        event_emitter=emitter,
    )

    dispatcher.registry.register(
        GovernanceRegressionCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_successful_execution_governance_regression():
    """
    Successful execution reaches COMPLETED and
    preserves transaction and observability semantics.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    handler = SuccessfulGovernanceHandler()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        GovernanceRegressionCommand(),
        build_context(),
    )

    assert result.is_success()

    assert handler.called is True

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


def test_failed_result_governance_regression():
    """
    A failed execution result reaches FAILED and
    rolls back the transaction.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    handler = FailedGovernanceHandler()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        GovernanceRegressionCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert result.error_code == (
        "REGRESSION_FAILURE"
    )

    assert handler.called is True

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


def test_handler_exception_governance_regression():
    """
    A handler exception reaches FAILED, rolls back
    the transaction, and preserves the original error.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    handler = ExceptionGovernanceHandler()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        transaction_boundary=transaction,
    )

    with pytest.raises(
        RuntimeError,
        match="governance regression failure",
    ):
        dispatcher.dispatch(
            GovernanceRegressionCommand(),
            build_context(),
        )

    assert handler.called is True

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


def test_authorization_denial_governance_regression():
    """
    Authorization denial reaches DENIED without
    executing the handler.
    """

    emitter = RecordingExecutionEventEmitter()

    handler = SuccessfulGovernanceHandler()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        authorizer=DenyingGovernanceAuthorizer(),
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceRegressionCommand(),
            build_context(),
        )

    assert handler.called is False

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.DENIED,
    ]


def test_authorization_denial_prevents_transaction():
    """
    Authorization denial occurs before the transaction
    boundary begins.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulGovernanceHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
        authorizer=DenyingGovernanceAuthorizer(),
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceRegressionCommand(),
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


def test_governance_aware_authorization_regression():
    """
    Governance-aware authorization uses the
    authorization service and produces a valid
    authorization decision.
    """

    service = ExecutionAuthorizationService(
        AllowingGovernanceAuthorizer()
    )

    governance = ExecutionGovernance()

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
            governance=governance,
        )
    )

    command = GovernanceRegressionCommand()

    context = build_context()

    decision = enforcement.authorize(
        command,
        context,
    )

    assert decision.is_allowed() is True

    event = enforcement.audit_event(
        command,
        context,
        decision,
    )

    assert event is not None

    result = enforcement.result(
        decision,
        context=context,
        message="Authorization succeeded.",
    )

    assert result.is_success()


def test_governance_aware_authorization_denial_regression():
    """
    Governance-aware authorization preserves a
    denied authorization decision and produces
    a governed failure result.
    """

    service = ExecutionAuthorizationService(
        DenyingGovernanceAuthorizer()
    )

    governance = ExecutionGovernance()

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
            governance=governance,
        )
    )

    command = GovernanceRegressionCommand()

    context = build_context()

    decision = enforcement.authorize(
        command,
        context,
    )

    assert decision.is_denied()

    result = enforcement.result(
        decision,
        context=context,
        message="Authorization denied.",
    )

    assert result.is_failure()

    assert result.error_code == (
        "AUTHORIZATION_DENIED"
    )


def test_governance_preserves_execution_context():
    """
    Dispatcher-generated governance events preserve
    the exact execution context.
    """

    emitter = RecordingExecutionEventEmitter()

    context = build_context()

    dispatcher = build_dispatcher(
        SuccessfulGovernanceHandler(),
        emitter=emitter,
    )

    dispatcher.dispatch(
        GovernanceRegressionCommand(),
        context,
    )

    assert len(emitter.events) == 2

    for event in emitter.events:
        assert event.context is context

        assert event.metadata["source"] == (
            "dispatcher"
        )


def test_dispatcher_remains_backward_compatible():
    """
    Optional governance infrastructure does not
    break the existing dispatcher behavior.
    """

    handler = SuccessfulGovernanceHandler()

    dispatcher = build_dispatcher(
        handler
    )

    result = dispatcher.dispatch(
        GovernanceRegressionCommand(),
        build_context(),
    )

    assert result.is_success()

    assert handler.called is True


def test_governance_regression_preserves_event_order():
    """
    Governance observability remains deterministic
    around transaction execution.
    """

    emitter = RecordingExecutionEventEmitter()

    transaction = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulGovernanceHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    dispatcher.dispatch(
        GovernanceRegressionCommand(),
        build_context(),
    )

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
