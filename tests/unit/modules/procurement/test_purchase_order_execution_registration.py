"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order workflow execution registration tests.
"""

from flask import Flask

from app.core.execution import (
    CommandDispatcher,
    command_registry,
)
from app.modules.procurement.commands import (
    ApprovePurchaseOrderCommand,
    CancelPurchaseOrderCommand,
    RejectPurchaseOrderCommand,
    ReturnPurchaseOrderCommand,
    SubmitPurchaseOrderCommand,
)
from app.modules.procurement.handlers import (
    ApprovePurchaseOrderHandler,
    CancelPurchaseOrderHandler,
    RejectPurchaseOrderHandler,
    ReturnPurchaseOrderHandler,
    SubmitPurchaseOrderHandler,
)
from app.modules.procurement.module import ProcurementModule


def test_procurement_module_exposes_purchase_order_execution_definitions():
    """
    Procurement exposes all approved Purchase Order workflow
    executions alongside other registered Procurement executions.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    purchase_order_commands = [
        definition.command
        for definition in definitions
        if definition.command in {
            SubmitPurchaseOrderCommand,
            ApprovePurchaseOrderCommand,
            RejectPurchaseOrderCommand,
            ReturnPurchaseOrderCommand,
            CancelPurchaseOrderCommand,
        }
    ]

    assert purchase_order_commands == [
        SubmitPurchaseOrderCommand,
        ApprovePurchaseOrderCommand,
        RejectPurchaseOrderCommand,
        ReturnPurchaseOrderCommand,
        CancelPurchaseOrderCommand,
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
        if item.command is SubmitPurchaseOrderCommand
    )

    assert isinstance(
        definition.handler,
        SubmitPurchaseOrderHandler,
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
        if item.command is ApprovePurchaseOrderCommand
    )

    assert isinstance(
        definition.handler,
        ApprovePurchaseOrderHandler,
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
        if item.command is RejectPurchaseOrderCommand
    )

    assert isinstance(
        definition.handler,
        RejectPurchaseOrderHandler,
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
        if item.command is ReturnPurchaseOrderCommand
    )

    assert isinstance(
        definition.handler,
        ReturnPurchaseOrderHandler,
    )


def test_cancel_command_is_paired_with_cancel_handler():
    """
    Cancel command is paired with its approved handler.
    """
    module = ProcurementModule()

    definitions = module.get_execution_definitions()

    definition = next(
        item
        for item in definitions
        if item.command is CancelPurchaseOrderCommand
    )

    assert isinstance(
        definition.handler,
        CancelPurchaseOrderHandler,
    )


def test_procurement_module_registers_purchase_order_commands():
    """
    All Procurement workflow commands register successfully,
    including the approved Purchase Order commands.
    """
    module = ProcurementModule()
    app = Flask(__name__)
    app.extensions["command_dispatcher"] = CommandDispatcher()

    command_registry.clear()

    try:
        module.register_execution(app)

        assert command_registry.count() == 9

        assert {
            "procurement.purchase_order.submit",
            "procurement.purchase_order.approve",
            "procurement.purchase_order.reject",
            "procurement.purchase_order.return",
            "procurement.purchase_order.cancel",
        }.issubset(
            set(command_registry.names())
        )

        assert (
            command_registry.get(
                "procurement.purchase_order.submit"
            )
            is SubmitPurchaseOrderCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_order.approve"
            )
            is ApprovePurchaseOrderCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_order.reject"
            )
            is RejectPurchaseOrderCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_order.return"
            )
            is ReturnPurchaseOrderCommand
        )
        assert (
            command_registry.get(
                "procurement.purchase_order.cancel"
            )
            is CancelPurchaseOrderCommand
        )
    finally:
        command_registry.clear()


def test_procurement_module_registers_purchase_order_handlers():
    """
    All Procurement workflow handlers register successfully,
    including the approved Purchase Order handlers.
    """
    module = ProcurementModule()
    app = Flask(__name__)
    dispatcher = CommandDispatcher()
    app.extensions["command_dispatcher"] = dispatcher

    command_registry.clear()

    try:
        module.register_execution(app)

        assert dispatcher.handler_count() == 9

        assert dispatcher.has_handler(
            SubmitPurchaseOrderCommand
        )
        assert dispatcher.has_handler(
            ApprovePurchaseOrderCommand
        )
        assert dispatcher.has_handler(
            RejectPurchaseOrderCommand
        )
        assert dispatcher.has_handler(
            ReturnPurchaseOrderCommand
        )
        assert dispatcher.has_handler(
            CancelPurchaseOrderCommand
        )

        assert isinstance(
            dispatcher.get_handler(
                SubmitPurchaseOrderCommand
            ),
            SubmitPurchaseOrderHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                ApprovePurchaseOrderCommand
            ),
            ApprovePurchaseOrderHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                RejectPurchaseOrderCommand
            ),
            RejectPurchaseOrderHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                ReturnPurchaseOrderCommand
            ),
            ReturnPurchaseOrderHandler,
        )
        assert isinstance(
            dispatcher.get_handler(
                CancelPurchaseOrderCommand
            ),
            CancelPurchaseOrderHandler,
        )
    finally:
        command_registry.clear()
