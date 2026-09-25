"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.9.2

Transaction-aware command dispatcher tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    CommandDispatcher,
    CommandRegistry,
    ExecutionContext,
    ExecutionResult,
    ExecutionTransactionBoundary,
    ExecutionContractException,
    PostCommitExecutor,
)

from app.core.execution.handlers.base import (
    BaseCommandHandler,
)


class TransactionTestCommand(BaseCommand):
    """
    Test command used for transaction-aware
    dispatcher tests.
    """

    command_name = (
        "test.transaction.dispatch"
    )

    permission_code = (
        "test.transaction.dispatch"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented by
        this command.
        """

        return self.command_name


class ValidTransactionTestHandler(
    BaseCommandHandler
):
    """
    Successful transaction test handler.
    """

    command_type = TransactionTestCommand

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
            }
        )


class FailingTransactionTestHandler(
    BaseCommandHandler
):
    """
    Handler that raises an exception during
    execution.
    """

    command_type = TransactionTestCommand

    def __init__(self):
        self.called = False

    def handle(
        self,
        command,
        context,
    ):
        self.called = True

        raise RuntimeError(
            "transaction execution failed"
        )


class TestTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Test transaction boundary recording
    lifecycle events.
    """

    def __init__(self):
        self.events = []

    def begin(self) -> None:
        self.events.append("begin")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")


class TestPostCommitExecutor(
    PostCommitExecutor
):
    """
    Test post-commit executor recording
    invocation and execution inputs.
    """

    def __init__(
        self,
        should_fail=False,
        boundary=None,
    ):
        self.should_fail = should_fail
        self.boundary = boundary
        self.calls = []
        self.events_at_execution = []

    def execute(
        self,
        command,
        context,
        result,
    ) -> None:
        if self.boundary is not None:
            self.events_at_execution = list(
                self.boundary.events
            )

        self.calls.append(
            (
                command,
                context,
                result,
            )
        )

        if self.should_fail:
            raise RuntimeError(
                "post-commit execution failed"
            )


class DenyingAuthorizer:
    """
    Test authorizer that denies execution.
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


def build_context() -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="transaction",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={},
    )


def build_dispatcher(
    handler,
    transaction_boundary=None,
    authorizer=None,
    post_commit_executor=None,
):
    """
    Build a dispatcher configured for the tests.
    """

    registry = CommandRegistry()

    registry.register(
        TransactionTestCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry,
        authorizer=authorizer,
        transaction_boundary=(
            transaction_boundary
        ),
        post_commit_executor=(
            post_commit_executor
        ),
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_dispatch_commits_transaction_after_successful_handler():
    """
    A successful command execution commits
    the transaction.
    """

    boundary = TestTransactionBoundary()

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True
    assert handler.called is True

    assert boundary.events == [
        "begin",
        "commit",
    ]


def test_dispatch_rolls_back_transaction_when_handler_fails():
    """
    A handler failure rolls back the transaction
    and preserves the original exception.
    """

    boundary = TestTransactionBoundary()

    handler = FailingTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
    )

    with pytest.raises(
        RuntimeError,
        match="transaction execution failed",
    ):
        dispatcher.dispatch(
            TransactionTestCommand(),
            build_context(),
        )

    assert handler.called is True

    assert boundary.events == [
        "begin",
        "rollback",
    ]


def test_dispatch_does_not_begin_transaction_when_authorization_is_denied():
    """
    Authorization denial occurs before the
    transaction boundary begins.
    """

    boundary = TestTransactionBoundary()

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
        authorizer=DenyingAuthorizer(),
    )

    with pytest.raises(
        ExecutionContractException,
    ):
        dispatcher.dispatch(
            TransactionTestCommand(),
            build_context(),
        )

    assert handler.called is False
    assert boundary.events == []


def test_dispatch_without_transaction_boundary_preserves_existing_behavior():
    """
    When no transaction boundary is configured,
    the handler executes normally.
    """

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True
    assert handler.called is True


def test_dispatcher_can_configure_transaction_boundary_after_initialization():
    """
    A transaction boundary can be configured
    after dispatcher initialization.
    """

    boundary = TestTransactionBoundary()

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler
    )

    dispatcher.set_transaction_boundary(
        boundary
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True

    assert boundary.events == [
        "begin",
        "commit",
    ]


def test_dispatcher_rejects_invalid_transaction_boundary():
    """
    Invalid transaction boundary objects are
    rejected by the dispatcher.
    """

    with pytest.raises(
        ExecutionContractException,
        match="Transaction boundary",
    ):
        CommandDispatcher(
            transaction_boundary=object()
        )


def test_dispatch_executes_post_commit_executor_after_transaction_commit():
    """
    Post-commit execution occurs only after
    the originating transaction commits.
    """

    boundary = TestTransactionBoundary()

    executor = TestPostCommitExecutor(
        boundary=boundary
    )

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
        post_commit_executor=executor,
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True

    assert boundary.events == [
        "begin",
        "commit",
    ]

    assert executor.events_at_execution == [
        "begin",
        "commit",
    ]

    assert len(executor.calls) == 1

    command, context, received_result = (
        executor.calls[0]
    )

    assert isinstance(
        command,
        TransactionTestCommand,
    )

    assert context.user_id == "user-001"

    assert received_result is result


def test_post_commit_failure_does_not_rollback_or_fail_command():
    """
    A post-commit failure cannot roll back
    an already-committed transaction or change
    the successful command result.
    """

    boundary = TestTransactionBoundary()

    executor = TestPostCommitExecutor(
        should_fail=True
    )

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
        post_commit_executor=executor,
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True

    assert boundary.events == [
        "begin",
        "commit",
    ]

    assert len(executor.calls) == 1


def test_post_commit_executor_is_not_called_when_handler_fails():
    """
    Post-commit execution does not occur when
    the originating transaction fails.
    """

    boundary = TestTransactionBoundary()

    executor = TestPostCommitExecutor()

    handler = FailingTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
        post_commit_executor=executor,
    )

    with pytest.raises(
        RuntimeError,
        match="transaction execution failed",
    ):
        dispatcher.dispatch(
            TransactionTestCommand(),
            build_context(),
        )

    assert boundary.events == [
        "begin",
        "rollback",
    ]

    assert executor.calls == []


def test_post_commit_executor_is_not_called_without_transaction_boundary():
    """
    Post-commit execution requires a successful
    originating transaction commit.
    """

    executor = TestPostCommitExecutor()

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        post_commit_executor=executor,
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True
    assert executor.calls == []


def test_dispatcher_can_configure_post_commit_executor_after_initialization():
    """
    A post-commit executor can be configured
    after dispatcher initialization.
    """

    boundary = TestTransactionBoundary()

    executor = TestPostCommitExecutor()

    handler = ValidTransactionTestHandler()

    dispatcher = build_dispatcher(
        handler,
        transaction_boundary=boundary,
    )

    dispatcher.set_post_commit_executor(
        executor
    )

    result = dispatcher.dispatch(
        TransactionTestCommand(),
        build_context(),
    )

    assert result.is_success() is True

    assert boundary.events == [
        "begin",
        "commit",
    ]

    assert len(executor.calls) == 1


def test_dispatcher_rejects_invalid_post_commit_executor():
    """
    Invalid post-commit executor objects are
    rejected by the dispatcher.
    """

    with pytest.raises(
        ExecutionContractException,
        match="Post-commit executor",
    ):
        CommandDispatcher(
            post_commit_executor=object()
        )
