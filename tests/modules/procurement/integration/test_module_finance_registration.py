"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement module Finance post-commit registration tests.
"""

from __future__ import annotations

from flask import Flask

from app.core.execution.dispatcher import (
    CommandDispatcher,
)
from app.core.startup.modules import (
    initialize_modules,
)
from app.modules.procurement.integration.post_commit import (
    ProcurementFinancePostCommitExecutor,
)


def test_module_startup_registers_procurement_finance_post_commit_executor():
    """
    Verify that enterprise startup composes the Procurement
    Finance post-commit executor onto the existing dispatcher.
    """

    app = Flask(__name__)

    manager = initialize_modules(app)

    assert manager is not None

    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    assert isinstance(
        dispatcher,
        CommandDispatcher,
    )

    assert isinstance(
        dispatcher.post_commit_executor,
        ProcurementFinancePostCommitExecutor,
    )
