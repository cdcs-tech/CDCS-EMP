"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.6

Governance and transaction integration tests.
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

from app.core.execution.event_emitter import (
    RecordingExecutionEventEmitter,
)

from app.core.execution.events import (
    ExecutionEventType,
)

from app.core.execution.transaction import (
    ExecutionTransactionBoundary,
)


class GovernanceTransactionCommand(
    BaseCommand
):
    """
    Test command used for governance and
    transaction integration tests.
    """

    command_name = (
        "test.governance.transaction"
    )

    permission_code = (
        "test.governance.transaction"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented by
        this command.
        """

        return self.command_name


class SuccessfulTransactionHandler(
    BaseCommandHandler
):
    """
    Handler returning a successful result.
    """

    command_type = (
        GovernanceTransactionCommand
    )

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


class FailedTransactionHandler(
    BaseCommandHandler
):
    """
    Handler returning a failed result.
    """

    command_type = (
        GovernanceTransactionCommand
    )

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
            error_code="TRANSACTION_FAILURE",
        )


class ExceptionTransactionHandler(
    BaseCommandHandler
):
    """
    Handler raising an execution exception.
    """

    command_type = (
        GovernanceTransactionCommand
    )

    def __init__(self):
        self.called = False

    def handle(
        self,
        command,
        context,
    ):
        self.called = True

        raise RuntimeError(
            "transaction handler failed"
        )


class AllowingTransactionAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that allows execution.
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
                    "transaction-test"
                ),
            },
        )


class DenyingTransactionAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that denies execution.
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
                    "transaction-test"
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
    Ensure the shared command registry is isolated
    between tests.
    """

    from app.core.execution import (
        command_registry,
    )

    command_name = (
        GovernanceTransactionCommand.command_name
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


def build_context() -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="governance-transaction",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={},
    )


def build_dispatcher(
    handler,
    *,
    authorizer=None,
    emitter=None,
    transaction_boundary=None,
):
    """
    Build a dispatcher configured for governance
    and transaction tests.
    """

    dispatcher = CommandDispatcher(
        authorizer=(
            authorizer
            or AllowingTransactionAuthorizer()
        ),
        event_emitter=emitter,
        transaction_boundary=(
            transaction_boundary
        ),
    )

    dispatcher.registry.register(
        GovernanceTransactionCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_governed_success_commits_transaction():
    """
    An authorized successful execution commits
    its transaction.
    """

    handler = SuccessfulTransactionHandler()

    transaction = RecordingTransactionBoundary()

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        GovernanceTransactionCommand(),
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


def test_governed_failed_result_rolls_back_transaction():
    """
    An authorized failed execution rolls back
    its transaction.
    """

    handler = FailedTransactionHandler()

    transaction = RecordingTransactionBoundary()

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        GovernanceTransactionCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert result.error_code == (
        "TRANSACTION_FAILURE"
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


def test_governed_handler_exception_rolls_back_transaction():
    """
    An authorized handler exception rolls back
    the transaction while preserving the original
    exception.
    """

    handler = ExceptionTransactionHandler()

    transaction = RecordingTransactionBoundary()

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        handler,
        emitter=emitter,
        transaction_boundary=transaction,
    )

    with pytest.raises(
        RuntimeError,
        match="transaction handler failed",
    ):
        dispatcher.dispatch(
            GovernanceTransactionCommand(),
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


def test_denied_governance_does_not_begin_transaction():
    """
    Authorization denial occurs before transaction
    execution begins.
    """

    handler = SuccessfulTransactionHandler()

    transaction = RecordingTransactionBoundary()

    emitter = RecordingExecutionEventEmitter()

    dispatcher = build_dispatcher(
        handler,
        authorizer=DenyingTransactionAuthorizer(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceTransactionCommand(),
            build_context(),
        )

    assert handler.called is False

    assert transaction.events == []

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.DENIED,
    ]


def test_transaction_begins_only_after_authorization():
    """
    The transaction boundary must not begin until
    authorization has succeeded.
    """

    sequence = []

    class OrderedAuthorizer(
        ExecutionAuthorizer
    ):
        def authorize(
            self,
            command,
            context,
        ):
            sequence.append(
                "authorize"
            )

            return AuthorizationDecision.allow(
                reason="Permission granted."
            )

    class OrderedTransactionBoundary(
        RecordingTransactionBoundary
    ):
        def begin(self):
            sequence.append("begin")
            super().begin()

    handler = SuccessfulTransactionHandler()

    transaction = OrderedTransactionBoundary()

    dispatcher = build_dispatcher(
        handler,
        authorizer=OrderedAuthorizer(),
        transaction_boundary=transaction,
    )

    dispatcher.dispatch(
        GovernanceTransactionCommand(),
        build_context(),
    )

    assert sequence == [
        "authorize",
        "begin",
    ]


def test_transaction_commit_precedes_completed_event():
    """
    A successful execution commits its transaction
    before the COMPLETED lifecycle event is emitted.
    """

    sequence = []

    class OrderedTransactionBoundary(
        RecordingTransactionBoundary
    ):
        def commit(self):
            sequence.append("commit")
            super().commit()

    class OrderedHandler(
        SuccessfulTransactionHandler
    ):
        def handle(
            self,
            command,
            context,
        ):
            sequence.append("handler")
            return super().handle(
                command,
                context,
            )

    class OrderedEmitter(
        RecordingExecutionEventEmitter
    ):
        def emit(self, event):
            sequence.append(
                event.event_type
            )

            super().emit(event)

    transaction = OrderedTransactionBoundary()

    emitter = OrderedEmitter()

    dispatcher = build_dispatcher(
        OrderedHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    dispatcher.dispatch(
        GovernanceTransactionCommand(),
        build_context(),
    )

    assert sequence == [
        ExecutionEventType.STARTED,
        "handler",
        "commit",
        ExecutionEventType.COMPLETED,
    ]


def test_transaction_rollback_precedes_failed_event():
    """
    A failed execution rolls back its transaction
    before the FAILED lifecycle event is emitted.
    """

    sequence = []

    class OrderedTransactionBoundary(
        RecordingTransactionBoundary
    ):
        def rollback(self):
            sequence.append("rollback")
            super().rollback()

    class OrderedHandler(
        FailedTransactionHandler
    ):
        def handle(
            self,
            command,
            context,
        ):
            sequence.append("handler")
            return super().handle(
                command,
                context,
            )

    class OrderedEmitter(
        RecordingExecutionEventEmitter
    ):
        def emit(self, event):
            sequence.append(
                event.event_type
            )

            super().emit(event)

    transaction = OrderedTransactionBoundary()

    emitter = OrderedEmitter()

    dispatcher = build_dispatcher(
        OrderedHandler(),
        emitter=emitter,
        transaction_boundary=transaction,
    )

    result = dispatcher.dispatch(
        GovernanceTransactionCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert sequence == [
        ExecutionEventType.STARTED,
        "handler",
        "rollback",
        ExecutionEventType.FAILED,
    ]


def test_governance_transaction_result_preserves_authorization_metadata():
    """
    Authorization metadata remains available on the
    authorization decision while transaction-aware
    execution proceeds normally.
    """

    authorizer = AllowingTransactionAuthorizer()

    command = GovernanceTransactionCommand()

    context = build_context()

    decision = authorizer.authorize(
        command,
        context,
    )

    assert decision.is_allowed()

    assert (
        decision.metadata[
            "authorization_source"
        ]
        == "transaction-test"
    )


def test_transaction_boundary_is_not_entered_when_authorization_fails():
    """
    A denied governance decision must prevent both
    handler execution and transaction initialization.
    """

    class GuardedTransactionBoundary(
        RecordingTransactionBoundary
    ):
        def begin(self):
            raise AssertionError(
                "Transaction began despite "
                "authorization denial."
            )

    handler = SuccessfulTransactionHandler()

    transaction = GuardedTransactionBoundary()

    dispatcher = build_dispatcher(
        handler,
        authorizer=DenyingTransactionAuthorizer(),
        transaction_boundary=transaction,
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceTransactionCommand(),
            build_context(),
        )

    assert handler.called is False
