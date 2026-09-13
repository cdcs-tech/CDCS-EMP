"""
Tests for Procurement Purchase Request execution registration.
"""

import pytest
from flask import Flask

from app.core.execution import (
    CommandDispatcher,
    command_registry,
)

from app.modules.procurement.commands import (
    ApprovePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
)

from app.modules.procurement.handlers import (
    ApprovePurchaseRequestHandler,
    SubmitPurchaseRequestHandler,
)

from app.modules.procurement.module import ProcurementModule


@pytest.fixture
def app():
    """Provide a minimal application for execution registration tests."""

    application = Flask(__name__)

    application.extensions[
        "command_dispatcher"
    ] = CommandDispatcher()

    return application


@pytest.fixture(autouse=True)
def clear_command_registry():
    """Keep the shared command registry isolated between tests."""

    command_registry.clear()

    yield

    command_registry.clear()


def test_procurement_module_exposes_purchase_request_execution_definitions():
    """Procurement exposes exactly the two approved Purchase Request commands."""

    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    assert len(definitions) == 2

    assert [
        definition.command.command_name
        for definition in definitions
    ] == [
        SubmitPurchaseRequestCommand.command_name,
        ApprovePurchaseRequestCommand.command_name,
    ]


def test_procurement_module_exposes_submit_purchase_request_handler():
    """Submit command is paired with its approved handler."""

    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    submit_definition = next(
        definition
        for definition in definitions
        if definition.command is SubmitPurchaseRequestCommand
    )

    assert isinstance(
        submit_definition.handler,
        SubmitPurchaseRequestHandler,
    )

    assert (
        submit_definition.handler.command_type
        is SubmitPurchaseRequestCommand
    )


def test_procurement_module_exposes_approve_purchase_request_handler():
    """Approve command is paired with its approved handler."""

    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    approve_definition = next(
        definition
        for definition in definitions
        if definition.command is ApprovePurchaseRequestCommand
    )

    assert isinstance(
        approve_definition.handler,
        ApprovePurchaseRequestHandler,
    )

    assert (
        approve_definition.handler.command_type
        is ApprovePurchaseRequestCommand
    )


def test_procurement_execution_registration_uses_enterprise_registry(
    app,
):
    """Procurement execution registration uses the enterprise registry."""

    module = ProcurementModule()

    module.register_execution(
        app
    )

    assert (
        command_registry.get(
            SubmitPurchaseRequestCommand.command_name
        )
        is SubmitPurchaseRequestCommand
    )

    assert (
        command_registry.get(
            ApprovePurchaseRequestCommand.command_name
        )
        is ApprovePurchaseRequestCommand
    )


def test_procurement_execution_registration_registers_handlers(
    app,
):
    """Procurement execution registration registers both handlers."""

    module = ProcurementModule()

    module.register_execution(
        app
    )

    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    assert (
        dispatcher.has_handler(
            SubmitPurchaseRequestCommand
        )
        is True
    )

    assert (
        dispatcher.has_handler(
            ApprovePurchaseRequestCommand
        )
        is True
    )
