"""
Command dispatcher tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    CommandRegistry,
    ExecutionContext,
    ExecutionResult,
    ExecutionContractException,
    HandlerContractException,
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


class CreateInvoiceHandler(
    BaseCommandHandler
):

    command_type = (
        CreateInvoiceCommand
    )

    def handle(
        self,
        command,
        context,
    ):

        return ExecutionResult.success_result(
            data={
                "invoice_created": True,
                "amount": command.amount,
            },
            message="Invoice created.",
        )


class InvalidResultHandler(
    BaseCommandHandler
):

    command_type = (
        CreateInvoiceCommand
    )

    def handle(
        self,
        command,
        context,
    ):

        return "invalid-result"


def build_dispatcher():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry
    )

    dispatcher.register_handler(
        CreateInvoiceHandler()
    )

    return dispatcher


def build_context():

    return ExecutionContext(
        user_id="user-001",
        module_name="finance",
        operation="create_invoice",
        request_id="req-001",
    )


def test_dispatcher_creation():

    dispatcher = CommandDispatcher()

    assert (
        dispatcher.handler_count()
        == 0
    )


def test_handler_registration():

    dispatcher = build_dispatcher()

    assert (
        dispatcher.handler_count()
        == 1
    )

    assert (
        dispatcher.has_handler(
            CreateInvoiceCommand
        )
        is True
    )


def test_handler_lookup():

    dispatcher = build_dispatcher()

    handler = dispatcher.get_handler(
        CreateInvoiceCommand
    )

    assert isinstance(
        handler,
        CreateInvoiceHandler,
    )


def test_command_dispatch():

    dispatcher = build_dispatcher()

    command = CreateInvoiceCommand(
        250.0
    )

    result = dispatcher.dispatch(
        command,
        build_context(),
    )

    assert (
        result.is_success()
        is True
    )

    assert (
        result.data[
            "invoice_created"
        ]
        is True
    )

    assert (
        result.data[
            "amount"
        ]
        == 250.0
    )


def test_unregistered_command_fails():

    registry = CommandRegistry()

    dispatcher = CommandDispatcher(
        registry=registry
    )

    command = CreateInvoiceCommand(
        250.0
    )

    with pytest.raises(
        ExecutionContractException
    ):

        dispatcher.dispatch(
            command,
            build_context(),
        )


def test_missing_handler_fails():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry
    )

    command = CreateInvoiceCommand(
        250.0
    )

    with pytest.raises(
        HandlerContractException
    ):

        dispatcher.dispatch(
            command,
            build_context(),
        )


def test_invalid_context_fails():

    dispatcher = build_dispatcher()

    command = CreateInvoiceCommand(
        250.0
    )

    invalid_context = ExecutionContext(
        module_name="finance",
    )

    with pytest.raises(
        ExecutionContractException
    ):

        dispatcher.dispatch(
            command,
            invalid_context,
        )


def test_handler_support_is_checked():

    class OtherHandler(
        BaseCommandHandler
    ):

        command_type = (
            CreateInvoiceCommand
        )

        def supports(
            self,
            command,
        ):

            return False

        def handle(
            self,
            command,
            context,
        ):

            return ExecutionResult.success_result()

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry
    )

    dispatcher.register_handler(
        OtherHandler()
    )

    command = CreateInvoiceCommand(
        250.0
    )

    with pytest.raises(
        HandlerContractException
    ):

        dispatcher.dispatch(
            command,
            build_context(),
        )


def test_invalid_handler_result_fails():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry
    )

    dispatcher.register_handler(
        InvalidResultHandler()
    )

    command = CreateInvoiceCommand(
        250.0
    )

    with pytest.raises(
        HandlerContractException
    ):

        dispatcher.dispatch(
            command,
            build_context(),
        )


def test_unregister_handler():

    dispatcher = build_dispatcher()

    removed = dispatcher.unregister_handler(
        CreateInvoiceCommand
    )

    assert isinstance(
        removed,
        CreateInvoiceHandler,
    )

    assert (
        dispatcher.has_handler(
            CreateInvoiceCommand
        )
        is False
    )


def test_unregister_missing_handler_fails():

    dispatcher = CommandDispatcher()

    with pytest.raises(
        HandlerContractException
    ):

        dispatcher.unregister_handler(
            CreateInvoiceCommand
        )


def test_clear_handlers():

    dispatcher = build_dispatcher()

    assert (
        dispatcher.handler_count()
        == 1
    )

    dispatcher.clear_handlers()

    assert (
        dispatcher.handler_count()
        == 0
    )
