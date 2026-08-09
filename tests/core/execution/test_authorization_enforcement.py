"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.8.7

Authorization decision enforcement tests.
"""

import pytest

from app.core.execution import (
    AuthorizationDecision,
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionAuthorizer,
    ExecutionContext,
    ExecutionContractException,
    ExecutionResult,
)


class TestCommand(BaseCommand):
    """
    Test command used for authorization enforcement.
    """

    command_name = (
        "test.authorization_enforcement.sprint_1_13_8_7"
    )

    def execute_name(self) -> str:
        return self.command_name


class AllowHandler(BaseCommandHandler):
    """
    Test handler that records whether it was executed.
    """

    command_type = TestCommand

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
                "metadata": dict(
                    context.metadata
                ),
            }
        )


class AllowAuthorizer(
    ExecutionAuthorizer
):
    """
    Test authorizer that allows execution.
    """

    def authorize(
        self,
        command,
        context,
    ):
        return AuthorizationDecision.allow(
            reason="Execution authorized."
        )


class DenyAuthorizer(
    ExecutionAuthorizer
):
    """
    Test authorizer that denies execution.
    """

    def authorize(
        self,
        command,
        context,
    ):
        return AuthorizationDecision.deny(
            reason="Execution denied."
        )


def build_context():
    """
    Build a valid execution context for testing.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="authorization_enforcement",
    )


def register_command(
    dispatcher,
):
    """
    Register the test command with the
    dispatcher's command registry.
    """

    if not dispatcher.registry.exists(
        TestCommand.command_name
    ):
        dispatcher.registry.register(
            TestCommand
        )


def test_allowed_authorization_reaches_handler():
    """
    An allowed authorization decision must
    allow the handler to execute.
    """

    dispatcher = CommandDispatcher(
        authorizer=AllowAuthorizer()
    )

    handler = AllowHandler()

    register_command(
        dispatcher
    )

    dispatcher.register_handler(
        handler
    )

    result = dispatcher.dispatch(
        TestCommand(),
        build_context(),
    )

    assert result.is_success()

    assert handler.called is True


def test_denied_authorization_blocks_handler():
    """
    A denied authorization decision must prevent
    the handler from executing.
    """

    dispatcher = CommandDispatcher(
        authorizer=DenyAuthorizer()
    )

    handler = AllowHandler()

    register_command(
        dispatcher
    )

    dispatcher.register_handler(
        handler
    )

    with pytest.raises(
        ExecutionContractException,
        match="Execution denied.",
    ):
        dispatcher.dispatch(
            TestCommand(),
            build_context(),
        )

    assert handler.called is False


def test_authorization_occurs_before_handler_execution():
    """
    Authorization must be enforced before
    handler execution.
    """

    dispatcher = CommandDispatcher(
        authorizer=DenyAuthorizer()
    )

    handler = AllowHandler()

    register_command(
        dispatcher
    )

    dispatcher.register_handler(
        handler
    )

    with pytest.raises(
        ExecutionContractException,
        match="Execution denied.",
    ):
        dispatcher.dispatch(
            TestCommand(),
            build_context(),
        )

    assert handler.called is False
