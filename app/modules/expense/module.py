"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Business Module
"""

from app.core.execution import ExecutionDefinition
from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)
from app.core.workflow import WorkflowDefinition

from app.modules.expense.security import (
    EXPENSE_PERMISSIONS,
)


class ExpenseModule(BaseModule):
    """
    CDCS-EMP Expense Management business module.

    Provides the enterprise module boundary for reusable
    operational expense management, including approved
    Expense workflow and workflow execution registration.
    """

    def register_models(self, app):
        """
        Register Expense Management SQLAlchemy models.

        Importing the module-local model package ensures
        Expense models are attached to the existing SQLAlchemy
        metadata without exposing them through app.models.
        """

        from app.modules.expense.models import (
            Expense,
            ExpenseClassification,
        )

        # Keep explicit references so the imports are intentional
        # and remain visible to static analysis.
        _ = (
            ExpenseClassification,
            Expense,
        )

    def get_metadata(self) -> ModuleMetadata:
        """
        Return Expense Management module metadata.
        """

        return ModuleMetadata(
            code="EXPENSE",
            name="Expense Management",
            description=(
                "Reusable operational expense management "
                "capability for enterprise business operations."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-receipt",
            url_prefix="/expense",
            dependencies=[],
            permissions=[],
            navigation_enabled=True,
            dashboard_enabled=False,
            active=True,
        )

    def get_permissions(self):
        """
        Return Expense Management enterprise security permissions.

        Permission registration is delegated to the enterprise
        BaseModule lifecycle.
        """

        return list(
            EXPENSE_PERMISSIONS
        )

    def get_workflows(self):
        """
        Return Expense Management enterprise workflow definitions.

        Workflow registration is delegated to the enterprise
        BaseModule lifecycle.
        """

        from app.modules.expense.workflows import (
            ExpenseWorkflow,
        )

        return [
            WorkflowDefinition(
                module_name="EXPENSE",
                workflow_name="expense",
                workflow=ExpenseWorkflow(),
            ),
        ]

    def get_execution_definitions(self):
        """
        Return Expense Management workflow execution definitions.

        Workflow command authorization and transaction management
        remain owned by the enterprise execution dispatcher.
        """

        from app.modules.expense.commands import (
            ApproveExpenseCommand,
            CloseExpenseCommand,
            RejectExpenseCommand,
            ResubmitExpenseCommand,
            ReturnExpenseCommand,
            SubmitExpenseCommand,
        )

        from app.modules.expense.handlers import (
            ApproveExpenseHandler,
            CloseExpenseHandler,
            RejectExpenseHandler,
            ResubmitExpenseHandler,
            ReturnExpenseHandler,
            SubmitExpenseHandler,
        )

        return [
            ExecutionDefinition(
                command=SubmitExpenseCommand,
                handler=SubmitExpenseHandler(),
            ),
            ExecutionDefinition(
                command=ApproveExpenseCommand,
                handler=ApproveExpenseHandler(),
            ),
            ExecutionDefinition(
                command=RejectExpenseCommand,
                handler=RejectExpenseHandler(),
            ),
            ExecutionDefinition(
                command=ReturnExpenseCommand,
                handler=ReturnExpenseHandler(),
            ),
            ExecutionDefinition(
                command=ResubmitExpenseCommand,
                handler=ResubmitExpenseHandler(),
            ),
            ExecutionDefinition(
                command=CloseExpenseCommand,
                handler=CloseExpenseHandler(),
            ),
        ]

    def get_execution_permissions(self) -> dict[str, str]:
        """
        Return Expense Management execution permission mappings.

        Each approved Expense workflow command is explicitly
        mapped to its corresponding Expense workflow permission.

        Permission definitions remain owned by the Expense
        security boundary. This mapping only declares which
        permission is required to execute a command.
        """

        return {
            "expense.submit":
                "EXPENSE.EXPENSE.SUBMIT",
            "expense.approve":
                "EXPENSE.EXPENSE.APPROVE",
            "expense.reject":
                "EXPENSE.EXPENSE.REJECT",
            "expense.return":
                "EXPENSE.EXPENSE.RETURN",
            "expense.resubmit":
                "EXPENSE.EXPENSE.RESUBMIT",
            "expense.close":
                "EXPENSE.EXPENSE.CLOSE",
        }

    def register_blueprints(self, app):
        """
        Register the Expense Management HTTP blueprint.

        The blueprint is registered through the Enterprise
        Module Framework lifecycle.
        """

        from app.modules.expense.routes import (
            expense_bp,
        )

        app.register_blueprint(
            expense_bp,
            url_prefix=self.metadata.url_prefix,
        )


__all__ = [
    "ExpenseModule",
]
