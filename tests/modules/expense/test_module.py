"""
Tests for the Expense Management business module.
"""

from app.core.execution.registration import (
    validate_execution_definition,
)
from app.core.modules import BaseModule
from app.modules.expense import ExpenseModule
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
from app.modules.expense.security import (
    EXPENSE_PERMISSIONS,
)
from app.modules.expense.workflows import (
    ExpenseWorkflow,
)


def test_expense_module_inherits_base_module():
    """
    Verify that ExpenseModule uses the enterprise BaseModule contract.
    """

    module = ExpenseModule()

    assert isinstance(
        module,
        BaseModule,
    )


def test_expense_module_exposes_expected_metadata():
    """
    ExpenseModule exposes the approved enterprise module metadata.
    """

    module = ExpenseModule()

    metadata = module.get_metadata()

    assert metadata.code == "EXPENSE"
    assert metadata.name == "Expense Management"
    assert metadata.version == "1.0.0"
    assert metadata.author == "CDCS"
    assert metadata.category == "Business"
    assert metadata.icon == "bi-receipt"
    assert metadata.url_prefix == "/expense"
    assert metadata.dependencies == []
    assert metadata.navigation_enabled is True
    assert metadata.dashboard_enabled is False
    assert metadata.active is True


def test_expense_module_exposes_canonical_permissions():
    """
    ExpenseModule exposes the canonical Expense permission aggregate.
    """

    module = ExpenseModule()

    permissions = module.get_permissions()

    assert len(permissions) == len(
        EXPENSE_PERMISSIONS
    )

    assert {
        permission.code
        for permission in permissions
    } == {
        permission.code
        for permission in EXPENSE_PERMISSIONS
    }


def test_expense_module_registers_models():
    """
    Verify that Expense models remain registered through
    the standard module model-registration mechanism.
    """

    module = ExpenseModule()

    module.register_models(None)

    from app.modules.expense.models import (
        Expense,
        ExpenseClassification,
    )

    assert Expense.__tablename__ == "expenses"
    assert (
        ExpenseClassification.__tablename__
        == "expense_classifications"
    )


def test_expense_module_exposes_expense_workflow():
    """
    Verify that Expense exposes the approved Expense
    workflow definition.
    """

    module = ExpenseModule()

    assert module.has_workflows() is True
    assert len(module.workflows) == 1

    expense_workflow = module.workflows[0]

    assert isinstance(
        expense_workflow.workflow,
        ExpenseWorkflow,
    )

    assert expense_workflow.module_name == "EXPENSE"
    assert expense_workflow.workflow_name == "expense"


def test_expense_module_exposes_workflow_execution_definitions():
    """
    Verify that Expense exposes all six approved workflow
    command and handler registrations.
    """

    module = ExpenseModule()

    definitions = module.get_execution_definitions()

    expected = [
        (
            SubmitExpenseCommand,
            SubmitExpenseHandler,
        ),
        (
            ApproveExpenseCommand,
            ApproveExpenseHandler,
        ),
        (
            RejectExpenseCommand,
            RejectExpenseHandler,
        ),
        (
            ReturnExpenseCommand,
            ReturnExpenseHandler,
        ),
        (
            ResubmitExpenseCommand,
            ResubmitExpenseHandler,
        ),
        (
            CloseExpenseCommand,
            CloseExpenseHandler,
        ),
    ]

    assert len(definitions) == len(expected)

    for definition, (
        expected_command,
        expected_handler,
    ) in zip(
        definitions,
        expected,
    ):
        assert definition.command is expected_command
        assert isinstance(
            definition.handler,
            expected_handler,
        )

        validate_execution_definition(
            definition
        )


def test_expense_module_execution_definitions_have_matching_handlers():
    """
    Verify that every Expense workflow execution definition
    satisfies the enterprise command/handler type boundary.
    """

    module = ExpenseModule()

    for definition in module.get_execution_definitions():
        assert (
            definition.handler.command_type
            is definition.command
        )


def test_expense_module_exposes_workflow_execution_permissions():
    """
    Verify the complete approved Expense workflow
    command-to-permission mapping.
    """

    module = ExpenseModule()

    execution_permissions = (
        module.get_execution_permissions()
    )

    assert execution_permissions == {
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


def test_expense_module_workflow_execution_permissions_are_complete():
    """
    Verify that every registered Expense workflow command
    has exactly one execution permission mapping.
    """

    module = ExpenseModule()

    definitions = (
        module.get_execution_definitions()
    )

    execution_permissions = (
        module.get_execution_permissions()
    )

    expected_command_names = {
        "expense.submit",
        "expense.approve",
        "expense.reject",
        "expense.return",
        "expense.resubmit",
        "expense.close",
    }

    assert expected_command_names == set(
        execution_permissions
    )

    assert {
        definition.command.command_name
        for definition in definitions
    } == expected_command_names
