"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement module Finance post-commit registration tests.
"""

from __future__ import annotations

from flask import Flask

from app.core.execution import (
    CommandDispatcher,
    PostCommitCoordinator,
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
    Finance post-commit executor through the enterprise
    post-commit coordinator.
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
        PostCommitCoordinator,
    )

    executors = (
        dispatcher.post_commit_executor.executors()
    )

    assert any(
        isinstance(
            executor,
            ProcurementFinancePostCommitExecutor,
        )
        for executor in executors
    )
