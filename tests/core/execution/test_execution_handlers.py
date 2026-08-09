"""
Handler contract tests.
"""

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    ExecutionContext,
    ExecutionResult,
)


class TestCommand(
    BaseCommand
):

    command_name = "test.command"

    def execute_name(self) -> str:

        return self.command_name


class TestHandler(
    BaseCommandHandler
):

    command_type = TestCommand

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


def test_handler_supports_command():

    handler = TestHandler()

    command = TestCommand()

    assert (
        handler.supports(command)
        is True
    )


def test_handler_rejects_other_command():

    handler = TestHandler()

    class OtherCommand(
        BaseCommand
    ):

        command_name = "other.command"

        def execute_name(self) -> str:

            return self.command_name

    command = OtherCommand()

    assert (
        handler.supports(command)
        is False
    )


def test_handler_execution():

    handler = TestHandler()

    command = TestCommand()

    context = ExecutionContext(
        module_name="test",
        operation="command",
    )

    result = handler.handle(
        command,
        context,
    )

    assert (
        result.is_success()
        is True
    )

    assert (
        result.data["executed"]
        is True
    )
