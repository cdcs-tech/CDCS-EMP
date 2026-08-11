"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.9.3

Transaction result and failure semantics tests.
"""

from app.core.execution import (
    BaseCommand,
    CommandDispatcher,
    CommandRegistry,
    ExecutionContext,
    ExecutionResult,
    ExecutionTransactionBoundary,
)


from app.core.execution.handlers.base import (
    BaseCommandHandler,
)


class TransactionResultCommand(
    BaseCommand
):
    """
    Test command used for transaction
    result semantics.
    """

    command_name = (
        "test.transaction.result"
    )

    permission_code = (
        "test.transaction.result"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented
        by this command.
        """

        return self.command_name


class SuccessfulResultHandler(
    BaseCommandHandler
):
    """
    Handler returning a successful result.
    """

    command_type = TransactionResultCommand

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.success_result(
            data={
                "executed": True,
            }
        )


class FailedResultHandler(
    BaseCommandHandler
):
    """
    Handler returning a failed result.
    """

    command_type = TransactionResultCommand

    def handle(
        self,
        command,
        context,
    ):
        return ExecutionResult.failure_result(
            message="Business operation failed.",
            error_code="BUSINESS_FAILURE",
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


def build_context() -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="transaction-result",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={},
    )


def build_dispatcher(
    handler,
    boundary,
):
    """
    Build a dispatcher configured with
    the supplied handler and transaction
    boundary.
    """

    registry = CommandRegistry()

    registry.register(
        TransactionResultCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry,
        transaction_boundary=boundary,
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_successful_execution_result_commits_transaction():
    """
    A successful execution result commits
    the transaction.
    """

    boundary = TestTransactionBoundary()

    dispatcher = build_dispatcher(
        SuccessfulResultHandler(),
        boundary,
    )

    result = dispatcher.dispatch(
        TransactionResultCommand(),
        build_context(),
    )

    assert result.is_success() is True

    assert boundary.events == [
        "begin",
        "commit",
    ]


def test_failed_execution_result_rolls_back_transaction():
    """
    A failed execution result rolls back the
    transaction without raising an exception.
    """

    boundary = TestTransactionBoundary()

    dispatcher = build_dispatcher(
        FailedResultHandler(),
        boundary,
    )

    result = dispatcher.dispatch(
        TransactionResultCommand(),
        build_context(),
    )

    assert result.is_failure() is True

    assert result.error_code == (
        "BUSINESS_FAILURE"
    )

    assert result.message == (
        "Business operation failed."
    )

    assert boundary.events == [
        "begin",
        "rollback",
    ]
