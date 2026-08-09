"""
Command registry tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    CommandRegistry,
    CommandValidationException,
)


class CreateInvoiceCommand(
    BaseCommand
):

    command_name = (
        "finance.create_invoice"
    )

    def execute_name(self) -> str:

        return self.command_name


class UpdateInvoiceCommand(
    BaseCommand
):

    command_name = (
        "finance.update_invoice"
    )

    def execute_name(self) -> str:

        return self.command_name


class InvalidCommand:

    command_name = (
        "invalid.command"
    )


def test_registry_creation():

    registry = CommandRegistry()

    assert registry.count() == 0


def test_command_registration():

    registry = CommandRegistry()

    result = registry.register(
        CreateInvoiceCommand
    )

    assert (
        result
        is CreateInvoiceCommand
    )

    assert (
        registry.count()
        == 1
    )

    assert (
        registry.exists(
            "finance.create_invoice"
        )
        is True
    )


def test_command_lookup():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    command = registry.get(
        "finance.create_invoice"
    )

    assert (
        command
        is CreateInvoiceCommand
    )


def test_command_names():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    registry.register(
        UpdateInvoiceCommand
    )

    names = registry.names()

    assert (
        "finance.create_invoice"
        in names
    )

    assert (
        "finance.update_invoice"
        in names
    )


def test_command_all():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    commands = registry.all()

    assert (
        commands[
            "finance.create_invoice"
        ]
        is CreateInvoiceCommand
    )


def test_duplicate_registration_fails():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    with pytest.raises(
        CommandValidationException
    ):

        registry.register(
            CreateInvoiceCommand
        )


def test_invalid_command_class_fails():

    registry = CommandRegistry()

    with pytest.raises(
        CommandValidationException
    ):

        registry.register(
            InvalidCommand
        )


def test_missing_command_name_fails():

    registry = CommandRegistry()

    class MissingNameCommand(
        BaseCommand
    ):

        def execute_name(self) -> str:

            return "missing"

    with pytest.raises(
        CommandValidationException
    ):

        registry.register(
            MissingNameCommand
        )


def test_missing_command_lookup_fails():

    registry = CommandRegistry()

    with pytest.raises(
        CommandValidationException
    ):

        registry.get(
            "unknown.command"
        )


def test_unregister():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    removed = registry.unregister(
        "finance.create_invoice"
    )

    assert (
        removed
        is CreateInvoiceCommand
    )

    assert (
        registry.exists(
            "finance.create_invoice"
        )
        is False
    )

    assert (
        registry.count()
        == 0
    )


def test_unregister_missing_command_fails():

    registry = CommandRegistry()

    with pytest.raises(
        CommandValidationException
    ):

        registry.unregister(
            "missing.command"
        )


def test_clear():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    registry.register(
        UpdateInvoiceCommand
    )

    assert (
        registry.count()
        == 2
    )

    registry.clear()

    assert (
        registry.count()
        == 0
    )


def test_registry_decorator_registration():

    registry = CommandRegistry()

    @registry.register
    class DecoratedCommand(
        BaseCommand
    ):

        command_name = (
            "test.decorated"
        )

        def execute_name(self) -> str:

            return self.command_name

    assert (
        registry.exists(
            "test.decorated"
        )
        is True
    )

    assert (
        registry.get(
            "test.decorated"
        )
        is DecoratedCommand
    )


def test_registry_validation():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    registry.register(
        UpdateInvoiceCommand
    )

    registry.validate()
