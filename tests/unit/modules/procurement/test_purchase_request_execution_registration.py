"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Request workflow execution registration tests.
"""

from flask import Flask

from app.core.execution import (
    CommandDispatcher,
    command_registry,
)
from app.modules.procurement.commands import (
    ApprovePurchaseRequestCommand,
    RejectPurchaseRequestCommand,
    ReturnPurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
)
from app.modules.procurement.handlers import (
    ApprovePurchaseRequestHandler,
    RejectPurchaseRequestHandler,
    ReturnPurchaseRequestHandler,
    SubmitPurchaseRequestHandler,
)
from app.modules.procurement.module import (
    ProcurementModule,
)


def test_procurement_module_exposes_purchase_request_execution_definitions():
    """
    Procurement exposes all approved Purchase Request workflow
    executions alongside other registered Procurement executions.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    purchase_request_commands = [
        definition.command
        for definition in definitions
        if definition.command in {
            SubmitPurchaseRequestCommand,
            ApprovePurchaseRequestCommand,
            RejectPurchaseRequestCommand,
            ReturnPurchaseRequestCommand,
        }
    ]

    assert purchase_request_commands == [
        SubmitPurchaseRequestCommand,
        ApprovePurchaseRequestCommand,
        RejectPurchaseRequestCommand,
        ReturnPurchaseRequestCommand,
    ]


def test_submit_command_is_paired_with_submit_handler():
    """
    Submit command is paired with its approved handler.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    definition = next(
        item
        for item in definitions
        if item.command is SubmitPurchaseRequestCommand
    )

    assert isinstance(
        definition.handler,
        SubmitPurchaseRequestHandler,
    )


def test_approve_command_is_paired_with_approve_handler():
    """
    Approve command is paired with its approved handler.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    definition = next(
        item
        for item in definitions
        if item.command is ApprovePurchaseRequestCommand
    )

    assert isinstance(
        definition.handler,
        ApprovePurchaseRequestHandler,
    )


def test_reject_command_is_paired_with_reject_handler():
    """
    Reject command is paired with its approved handler.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    definition = next(
        item
        for item in definitions
        if item.command is RejectPurchaseRequestCommand
    )

    assert isinstance(
        definition.handler,
        RejectPurchaseRequestHandler,
    )


def test_return_command_is_paired_with_return_handler():
    """
    Return command is paired with its approved handler.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    definition = next(
        item
        for item in definitions
        if item.command is ReturnPurchaseRequestCommand
    )

    assert isinstance(
        definition.handler,
        ReturnPurchaseRequestHandler,
    )


def test_procurement_module_registers_purchase_request_commands():
    """
    All Procurement workflow commands register successfully,
    including the approved Purchase Request commands.
    """
    module = ProcurementModule()
    app = Flask(__name__)
    app.extensions["command_dispatcher"] = CommandDispatcher()

    command_registry.clear()

    try:
        module.register_execution(app)

        assert command_registry.count() == 10

        assert {
            "procurement.purchase_request.submit",
            "procurement.purchase_request.approve",
            "procurement.purchase_request.reject",
            "procurement.purchase_request.return",
        }.issubset(
            set(command_registry.names())
        )

        assert (
            command_registry.get(
                "procurement.purchase_request.submit"
            )
            is SubmitPurchaseRequestCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_request.approve"
            )
            is ApprovePurchaseRequestCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_request.reject"
            )
            is RejectPurchaseRequestCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_request.return"
            )
            is ReturnPurchaseRequestCommand
        )
    finally:
        command_registry.clear()


def test_procurement_module_registers_purchase_request_handlers():
    """
    All Procurement workflow handlers register successfully,
    including the approved Purchase Request handlers.
    """
    module = ProcurementModule()
    app = Flask(__name__)
    dispatcher = CommandDispatcher()
    app.extensions["command_dispatcher"] = dispatcher

    command_registry.clear()

    try:
        module.register_execution(app)

        assert dispatcher.handler_count() == 10

        assert dispatcher.has_handler(
            SubmitPurchaseRequestCommand
        )
        assert dispatcher.has_handler(
            ApprovePurchaseRequestCommand
        )
        assert dispatcher.has_handler(
            RejectPurchaseRequestCommand
        )
        assert dispatcher.has_handler(
            ReturnPurchaseRequestCommand
        )

        assert isinstance(
            dispatcher.get_handler(
                SubmitPurchaseRequestCommand
            ),
            SubmitPurchaseRequestHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                ApprovePurchaseRequestCommand
            ),
            ApprovePurchaseRequestHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                RejectPurchaseRequestCommand
            ),
            RejectPurchaseRequestHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                ReturnPurchaseRequestCommand
            ),
            ReturnPurchaseRequestHandler,
        )
    finally:
        command_registry.clear()
