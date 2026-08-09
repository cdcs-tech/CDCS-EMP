"""
Execution contract tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    ExecutionContext,
    ExecutionResult,
    validate_execution_contract,
    validate_execution_result,
)


class TestCommand(
    BaseCommand
):

    command_name = "test.command"

    def execute_name(self) -> str:

        return self.command_name


def test_valid_execution_contract():

    command = TestCommand()

    context = ExecutionContext(
        module_name="test",
        operation="command",
    )

    validate_execution_contract(
        command,
        context,
    )


def test_invalid_command_type():

    context = ExecutionContext(
        module_name="test",
        operation="command",
    )

    with pytest.raises(
        TypeError
    ):

        validate_execution_contract(
            object(),
            context,
        )


def test_invalid_context_type():

    command = TestCommand()

    with pytest.raises(
        TypeError
    ):

        validate_execution_contract(
            command,
            object(),
        )


def test_valid_execution_result():

    result = ExecutionResult.success_result()

    validate_execution_result(
        result
    )


def test_invalid_execution_result():

    with pytest.raises(
        TypeError
    ):

        validate_execution_result(
            object()
        )
