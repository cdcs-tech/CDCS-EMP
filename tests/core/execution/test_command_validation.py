"""
Command validation tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    CommandMetadata,
    CommandType,
    CommandValidationException,
    validate_command,
)


class CreateInvoiceCommand(
    BaseCommand
):

    command_name = (
        "finance.create_invoice"
    )

    command_type = (
        CommandType.CREATE
    )

    metadata = CommandMetadata(
        name="create_invoice",
        module_name="finance",
        operation="create_invoice",
    )

    def __init__(
        self,
        amount: float,
    ):

        self.amount = amount

    def execute_name(self) -> str:

        return self.command_name


def test_command_type():

    command = CreateInvoiceCommand(
        250.0
    )

    assert (
        command.command_type
        == CommandType.CREATE
    )


def test_command_metadata():

    command = CreateInvoiceCommand(
        250.0
    )

    metadata = (
        command.command_metadata()
    )

    assert metadata is not None

    assert (
        metadata.module_name
        == "finance"
    )


def test_command_qualified_name():

    command = CreateInvoiceCommand(
        250.0
    )

    assert (
        command.qualified_name()
        == "finance.create_invoice"
    )


def test_command_validation():

    command = CreateInvoiceCommand(
        250.0
    )

    validate_command(
        command
    )


def test_invalid_command():

    with pytest.raises(
        CommandValidationException
    ):

        validate_command(
            object()
        )
