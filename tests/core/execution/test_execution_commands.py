"""
Command contract tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    CommandValidationException,
)


class CreateInvoiceCommand(
    BaseCommand
):

    command_name = (
        "finance.create_invoice"
    )

    def __init__(
        self,
        amount: float,
    ):
        self.amount = amount

    def execute_name(self) -> str:

        return self.command_name


def test_command_creation():

    command = CreateInvoiceCommand(
        250.0
    )

    assert (
        command.execute_name()
        == "finance.create_invoice"
    )

    command.validate()


def test_command_payload():

    command = CreateInvoiceCommand(
        250.0
    )

    payload = command.payload()

    assert (
        payload["amount"]
        == 250.0
    )


def test_command_requires_name():

    class InvalidCommand(
        BaseCommand
    ):

        def execute_name(self) -> str:

            return "invalid"

    command = InvalidCommand()

    with pytest.raises(
        CommandValidationException
    ):
        command.validate()

from app.core.execution import (
    CommandMetadata,
    CommandType,
)


def test_base_command_default_type():

    command = CreateInvoiceCommand(
        250.0
    )

    assert (
        command.command_type
        == CommandType.EXECUTE
    )


def test_base_command_qualified_name():

    command = CreateInvoiceCommand(
        250.0
    )

    assert (
        command.qualified_name()
        == command.command_name
    )


def test_base_command_metadata_is_optional():

    command = CreateInvoiceCommand(
        250.0
    )

    assert (
        command.command_metadata()
        is None
    )


def test_command_payload_remains_compatible():

    command = CreateInvoiceCommand(
        250.0
    )

    payload = command.payload()

    assert (
        payload["amount"]
        == 250.0
    )
