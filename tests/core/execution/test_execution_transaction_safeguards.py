"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.9.4

Execution transaction integration and safeguard tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    CommandRegistry,
    ExecutionContext,
    ExecutionContractException,
    ExecutionResult,
    ExecutionTransactionBoundary,
)

from app.core.crud.transaction import (
    SimpleTransactionManager,
)

from app.core.execution.transaction import (
    CRUDTransactionBoundary,
)


class SafeguardCommand(BaseCommand):
    """
    Test command used for transaction safeguard tests.
    """

    command_name = "test.transaction.safeguard"
    permission_code = "test.transaction.safeguard"

    def execute_name(self) -> str:
        """
        Return the operation represented by this command.
        """

        return self.command_name


class SuccessfulHandler(BaseCommandHandler):
    """
    Handler returning a successful execution result.
    """

    command_type = SafeguardCommand

    def handle(self, command, context):
        return ExecutionResult.success_result(
            data={"executed": True},
            message="Execution completed.",
        )


class FailedResultHandler(BaseCommandHandler):
    """
    Handler returning a failed execution result.
    """

    command_type = SafeguardCommand

    def handle(self, command, context):
        return ExecutionResult.failure_result(
            message="Execution failed.",
            error_code="TEST_FAILURE",
        )


class ExceptionHandler(BaseCommandHandler):
    """
    Handler raising an exception during execution.
    """

    command_type = SafeguardCommand

    def handle(self, command, context):
        raise RuntimeError(
            "handler execution failed"
        )


class RecordingTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Transaction boundary that records lifecycle events.
    """

    def __init__(self):
        self.events = []

    def begin(self):
        self.events.append("begin")

    def commit(self):
        self.events.append("commit")

    def rollback(self):
        self.events.append("rollback")


class FailingCommitBoundary(
    RecordingTransactionBoundary
):
    """
    Transaction boundary whose commit operation fails.
    """

    def commit(self):
        self.events.append("commit")
        raise RuntimeError("commit failed")


class FailingRollbackBoundary(
    RecordingTransactionBoundary
):
    """
    Transaction boundary whose rollback operation fails.
    """

    def rollback(self):
        self.events.append("rollback")
        raise RuntimeError("rollback failed")


def build_dispatcher(
    handler,
    transaction_boundary=None,
):
    """
    Build an isolated dispatcher for safeguard tests.

    Each test receives a fresh command registry so that
    command registration does not leak between tests.
    """

    registry = CommandRegistry()

    dispatcher = CommandDispatcher(
        registry=registry,
        transaction_boundary=transaction_boundary,
    )

    dispatcher.registry.register(
        SafeguardCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def build_context():
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
    )


def test_invalid_transaction_boundary_is_rejected():
    """
    Dispatcher rejects an invalid transaction boundary.
    """

    with pytest.raises(
        ExecutionContractException,
        match="Transaction boundary",
    ):
        CommandDispatcher(
            transaction_boundary=object()
        )


def test_set_transaction_boundary_rejects_invalid_boundary():
    """
    Runtime transaction-boundary configuration rejects
    invalid objects.
    """

    dispatcher = CommandDispatcher()

    with pytest.raises(
        ExecutionContractException,
        match="Transaction boundary",
    ):
        dispatcher.set_transaction_boundary(
            object()
        )


def test_successful_execution_commits_transaction():
    """
    Successful execution follows begin -> commit.
    """

    boundary = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        boundary,
    )

    result = dispatcher.dispatch(
        SafeguardCommand(),
        build_context(),
    )

    assert result.is_success()

    assert boundary.events == [
        "begin",
        "commit",
    ]


def test_failed_execution_result_rolls_back_transaction():
    """
    A failed execution result rolls back the transaction
    and is returned to the caller.
    """

    boundary = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        FailedResultHandler(),
        boundary,
    )

    result = dispatcher.dispatch(
        SafeguardCommand(),
        build_context(),
    )

    assert result.is_failure()

    assert result.error_code == "TEST_FAILURE"

    assert boundary.events == [
        "begin",
        "rollback",
    ]


def test_handler_exception_rolls_back_and_is_preserved():
    """
    A handler exception rolls back the transaction and
    preserves the original exception.
    """

    boundary = RecordingTransactionBoundary()

    dispatcher = build_dispatcher(
        ExceptionHandler(),
        boundary,
    )

    with pytest.raises(
        RuntimeError,
        match="handler execution failed",
    ):
        dispatcher.dispatch(
            SafeguardCommand(),
            build_context(),
        )

    assert boundary.events == [
        "begin",
        "rollback",
    ]


def test_commit_failure_is_not_silently_ignored():
    """
    A commit failure is propagated to the caller.
    """

    boundary = FailingCommitBoundary()

    dispatcher = build_dispatcher(
        SuccessfulHandler(),
        boundary,
    )

    with pytest.raises(
        RuntimeError,
        match="commit failed",
    ):
        dispatcher.dispatch(
            SafeguardCommand(),
            build_context(),
        )

    assert boundary.events == [
        "begin",
        "commit",
        "rollback",
    ]


def test_crud_transaction_boundary_delegates_lifecycle():
    """
    CRUDTransactionBoundary delegates transaction lifecycle
    operations to the existing CRUD transaction manager.
    """

    manager = SimpleTransactionManager()

    boundary = CRUDTransactionBoundary(
        manager
    )

    boundary.begin()

    assert manager.active is True

    boundary.commit()

    assert manager.active is False
    assert manager.committed is True
    assert manager.rolled_back is False


def test_crud_transaction_boundary_rolls_back():
    """
    CRUDTransactionBoundary delegates rollback correctly.
    """

    manager = SimpleTransactionManager()

    boundary = CRUDTransactionBoundary(
        manager
    )

    boundary.begin()
    boundary.rollback()

    assert manager.active is False
    assert manager.committed is False
    assert manager.rolled_back is True
