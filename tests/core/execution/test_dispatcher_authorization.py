"""
Tests for dispatcher authorization integration.
"""

from app.core.execution.authorization import (
    AuthorizationDecision,
    ExecutionAuthorizer,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.commands.registry import (
    CommandRegistry,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.dispatcher import (
    CommandDispatcher,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)

from app.core.execution.handlers.base import (
    BaseCommandHandler,
)

from app.core.execution.results import (
    ExecutionResult,
)


class TestCommand(BaseCommand):
    """
    Test command.
    """

    command_name = "test.dispatch.authorization"

    def execute_name(self) -> str:
        return "test.dispatch.authorization"


class TestHandler(BaseCommandHandler):
    """
    Test command handler.
    """

    command_type = TestCommand

    called = False

    def handle(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> ExecutionResult:
        self.called = True

        return ExecutionResult.success_result(
            data={
                "metadata": dict(
                    context.metadata
                )
            }
        )


class DenyAuthorizer(ExecutionAuthorizer):
    """
    Authorizer that always denies.
    """

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        return AuthorizationDecision.deny(
            reason="Execution denied for testing."
        )


class AllowAuthorizer(ExecutionAuthorizer):
    """
    Authorizer that always allows.
    """

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        return AuthorizationDecision.allow(
            reason="Execution allowed for testing."
        )


def create_dispatcher(
    authorizer: ExecutionAuthorizer,
):
    """
    Create a dispatcher with isolated registry
    and test handler.
    """

    registry = CommandRegistry()

    registry.register(
        TestCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry,
        authorizer=authorizer,
    )

    handler = TestHandler()

    dispatcher.register_handler(
        handler
    )

    return dispatcher, handler


def create_context():
    """
    Create a valid execution context.
    """

    return ExecutionContext(
        user_id="test-user",
        module_name="test",
        operation="dispatch_authorization",
        metadata={
            "original": True,
        },
    )


def test_authorized_command_reaches_handler():
    """
    An authorized command reaches its handler.
    """

    dispatcher, handler = create_dispatcher(
        AllowAuthorizer()
    )

    result = dispatcher.dispatch(
        TestCommand(),
        create_context(),
    )

    assert result.is_success()
    assert handler.called is True


def test_denied_command_does_not_reach_handler():
    """
    A denied command must never reach its handler.
    """

    dispatcher, handler = create_dispatcher(
        DenyAuthorizer()
    )

    try:
        dispatcher.dispatch(
            TestCommand(),
            create_context(),
        )

        assert False, (
            "Expected authorization to fail."
        )

    except ExecutionContractException as exc:
        assert (
            "Execution denied for testing."
            in str(exc)
        )

    assert handler.called is False


def test_authorization_can_be_replaced():
    """
    The dispatcher supports replacing its authorizer.
    """

    dispatcher, handler = create_dispatcher(
        DenyAuthorizer()
    )

    dispatcher.set_authorizer(
        AllowAuthorizer()
    )

    result = dispatcher.dispatch(
        TestCommand(),
        create_context(),
    )

    assert result.is_success()
    assert handler.called is True


def test_handler_context_remains_enriched():
    """
    Existing handler context enrichment is preserved.
    """

    dispatcher, handler = create_dispatcher(
        AllowAuthorizer()
    )

    result = dispatcher.dispatch(
        TestCommand(),
        create_context(),
    )

    metadata = result.data[
        "metadata"
    ]

    assert metadata["original"] is True
    assert metadata["command"] == (
        "test.dispatch.authorization"
    )
    assert metadata["handler"] == (
        "TestHandler"
    )


def test_authorizer_failure_is_converted_to_execution_contract_error():
    """
    Unexpected authorization failures are exposed
    as execution contract failures.
    """

    class BrokenAuthorizer(
        ExecutionAuthorizer
    ):
        def authorize(
            self,
            command: BaseCommand,
            context: ExecutionContext,
        ) -> AuthorizationDecision:
            raise RuntimeError(
                "Unexpected security failure."
            )

    dispatcher, handler = create_dispatcher(
        BrokenAuthorizer()
    )

    try:
        dispatcher.dispatch(
            TestCommand(),
            create_context(),
        )

        assert False, (
            "Expected authorization failure."
        )

    except ExecutionContractException as exc:
        assert (
            "Authorization evaluation failed."
            in str(exc)
        )

    assert handler.called is False
