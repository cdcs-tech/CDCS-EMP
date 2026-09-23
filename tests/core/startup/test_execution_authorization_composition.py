"""
CDCS Enterprise Management Platform (CDCS-EMP)

Execution authorization composition and Procurement/Expense
workflow authorization-path tests.
"""

import pytest

from app.extensions import db

from app.models import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)

from app.core.execution.commands.registry import (
    command_registry,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)

from app.core.execution.policy import (
    PermissionAwareExecutionAuthorizer,
)

from app.core.execution.results import (
    ExecutionResult,
)

from app.core.execution.security import (
    RegistryBackedPermissionExecutionPolicy,
)

from app.modules.expense.commands import (
    SubmitExpenseCommand,
)

from app.modules.expense.module import (
    ExpenseModule,
)

from app.modules.procurement.commands import (
    SubmitPurchaseOrderCommand,
    SubmitPurchaseRequestCommand,
)

from app.modules.procurement.module import (
    ProcurementModule,
)


def test_application_exposes_execution_permission_policy(app):
    """
    Application startup exposes the composed execution
    permission policy through application extensions.
    """
    policy = app.extensions.get(
        "execution_permission_policy"
    )

    assert isinstance(
        policy,
        RegistryBackedPermissionExecutionPolicy,
    )


def test_procurement_execution_permissions_are_composed_into_policy(
    app,
):
    """
    Procurement execution-permission declarations are
    composed into the application execution policy.
    """
    policy = app.extensions[
        "execution_permission_policy"
    ]

    expected = {
        "procurement.purchase_request.submit":
        "PROCUREMENT.PURCHASE_REQUEST.SUBMIT",
        "procurement.purchase_request.approve":
        "PROCUREMENT.PURCHASE_REQUEST.APPROVE",
        "procurement.purchase_request.reject":
        "PROCUREMENT.PURCHASE_REQUEST.REJECT",
        "procurement.purchase_request.return":
        "PROCUREMENT.PURCHASE_REQUEST.RETURN",
    }

    for command_name, permission_code in expected.items():
        resolved_permission = (
            policy._permissions.get(command_name)
        )

        assert resolved_permission is not None
        assert (
            resolved_permission.code
            == permission_code
        )


def test_expense_execution_permissions_are_composed_into_policy(
    app,
):
    """
    All six Expense workflow execution-permission declarations
    are composed into the application execution policy.
    """
    policy = app.extensions[
        "execution_permission_policy"
    ]

    expected = {
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

    for command_name, permission_code in expected.items():
        resolved_permission = (
            policy._permissions.get(command_name)
        )

        assert resolved_permission is not None
        assert (
            resolved_permission.code
            == permission_code
        )


def test_execution_permission_policy_validates_against_security_registry(
    app,
):
    """
    Composed execution permissions resolve against the
    enterprise security permission registry.
    """
    policy = app.extensions[
        "execution_permission_policy"
    ]

    policy.validate_registered_permissions()


def test_command_dispatcher_uses_permission_aware_authorizer(
    app,
):
    """
    Application startup configures the command dispatcher
    with the permission-aware execution authorizer.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    assert isinstance(
        dispatcher.authorizer,
        PermissionAwareExecutionAuthorizer,
    )


def test_procurement_execution_permission_declarations_match_module_contract(
    app,
):
    """
    Startup-composed Procurement mappings match the
    Procurement module execution-permission contract.
    """
    module = ProcurementModule()

    policy = app.extensions[
        "execution_permission_policy"
    ]

    composed_permissions = {
        command_name: policy._permissions[
            command_name
        ].code
        for command_name in (
            module.get_execution_permissions()
        )
    }

    assert (
        composed_permissions
        == module.get_execution_permissions()
    )


def test_expense_execution_permission_declarations_match_module_contract(
    app,
):
    """
    Startup-composed Expense mappings match the
    Expense module execution-permission contract.
    """
    module = ExpenseModule()

    policy = app.extensions[
        "execution_permission_policy"
    ]

    composed_permissions = {
        command_name: policy._permissions[
            command_name
        ].code
        for command_name in (
            module.get_execution_permissions()
        )
    }

    assert (
        composed_permissions
        == module.get_execution_permissions()
    )


def test_expense_workflow_commands_and_handlers_are_registered(
    app,
):
    """
    Expense workflow commands are registered with the enterprise
    command registry and their handlers are available through the
    application dispatcher.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    expected_commands = {
        "expense.submit": SubmitExpenseCommand,
    }

    for command_name, command_type in expected_commands.items():
        assert command_registry.exists(
            command_name
        )

        assert dispatcher.has_handler(
            command_type
        )


def test_unauthorized_purchase_request_submit_is_denied_before_handler(
    app,
    regular_user,
):
    """
    A user without the Purchase Request SUBMIT permission
    is denied before the registered handler is invoked.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    command_name = (
        "procurement.purchase_request.submit"
    )

    assert command_registry.exists(
        command_name
    )

    command = SubmitPurchaseRequestCommand(
        purchase_request_id=1
    )

    context = ExecutionContext(
        user_id=str(
            regular_user.id
        ),
        module_name="PROCUREMENT",
        operation="purchase_request.submit",
        metadata={
            "source": "authorization-test",
        },
    )

    handler = dispatcher.get_handler(
        type(command)
    )

    assert handler is not None

    handler_called = False
    original_handle = handler.handle

    def tracked_handle(
        command,
        context,
    ):
        nonlocal handler_called

        handler_called = True

        return original_handle(
            command,
            context,
        )

    handler.handle = tracked_handle

    try:
        with pytest.raises(
            ExecutionContractException
        ):
            dispatcher.dispatch(
                command,
                context,
            )

        assert handler_called is False

    finally:
        handler.handle = original_handle


def test_unauthorized_purchase_order_submit_is_denied_before_handler(
    app,
    regular_user,
):
    """
    A user without the Purchase Order SUBMIT permission
    is denied before the registered handler is invoked.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    command_name = (
        "procurement.purchase_order.submit"
    )

    assert command_registry.exists(
        command_name
    )

    command = SubmitPurchaseOrderCommand(
        purchase_order_id=1
    )

    context = ExecutionContext(
        user_id=str(
            regular_user.id
        ),
        module_name="PROCUREMENT",
        operation="purchase_order.submit",
        metadata={
            "source": "authorization-test",
        },
    )

    handler = dispatcher.get_handler(
        type(command)
    )

    assert handler is not None

    handler_called = False
    original_handle = handler.handle

    def tracked_handle(
        command,
        context,
    ):
        nonlocal handler_called

        handler_called = True

        return original_handle(
            command,
            context,
        )

    handler.handle = tracked_handle

    try:
        with pytest.raises(
            ExecutionContractException
        ):
            dispatcher.dispatch(
                command,
                context,
            )

        assert handler_called is False

    finally:
        handler.handle = original_handle


def test_unauthorized_expense_submit_is_denied_before_handler(
    app,
    regular_user,
):
    """
    A user without the Expense SUBMIT permission is denied
    before the registered Expense handler is invoked.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    command_name = "expense.submit"

    assert command_registry.exists(
        command_name
    )

    command = SubmitExpenseCommand(
        expense_id=1
    )

    context = ExecutionContext(
        user_id=str(
            regular_user.id
        ),
        module_name="EXPENSE",
        operation="expense.submit",
        metadata={
            "source": "authorization-test",
        },
    )

    handler = dispatcher.get_handler(
        type(command)
    )

    assert handler is not None

    handler_called = False
    original_handle = handler.handle

    def tracked_handle(
        command,
        context,
    ):
        nonlocal handler_called

        handler_called = True

        return original_handle(
            command,
            context,
        )

    handler.handle = tracked_handle

    try:
        with pytest.raises(
            ExecutionContractException
        ):
            dispatcher.dispatch(
                command,
                context,
            )

        assert handler_called is False

    finally:
        handler.handle = original_handle


def test_authorized_purchase_order_submit_reaches_handler(
    app,
    regular_user,
):
    """
    A user with the Purchase Order SUBMIT permission passes
    the real startup execution-authorization path and reaches
    the registered handler.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    permission = Permission.query.filter_by(
        name="procurement.purchase_order.submit"
    ).first()

    if permission is None:
        permission = Permission(
            name="procurement.purchase_order.submit",
            module="PROCUREMENT",
            description="Submit Procurement purchase orders.",
        )

        db.session.add(permission)
        db.session.flush()

    if not regular_user.user_roles:
        role = Role(
            name="Execution Authorization Test Role",
            description=(
                "Role used by the execution authorization "
                "integration test."
            ),
            is_system=False,
        )

        db.session.add(role)
        db.session.flush()

        user_role = UserRole(
            user=regular_user,
            role=role,
        )

        db.session.add(user_role)
        db.session.flush()

    else:
        role = regular_user.user_roles[0].role

    existing_role_permission = RolePermission.query.filter_by(
        role_id=role.id,
        permission_id=permission.id,
    ).first()

    if existing_role_permission is None:
        role_permission = RolePermission(
            role=role,
            permission=permission,
        )

        db.session.add(role_permission)

    db.session.commit()

    assert regular_user.has_permission(
        "PROCUREMENT.PURCHASE_ORDER.SUBMIT"
    ) is True

    command_name = (
        "procurement.purchase_order.submit"
    )

    assert command_registry.exists(
        command_name
    )

    command = SubmitPurchaseOrderCommand(
        purchase_order_id=1
    )

    context = ExecutionContext(
        user_id=str(
            regular_user.id
        ),
        module_name="PROCUREMENT",
        operation="purchase_order.submit",
        metadata={
            "source": "authorization-test",
        },
    )

    handler = dispatcher.get_handler(
        type(command)
    )

    assert handler is not None

    handler_called = False
    original_handle = handler.handle

    def tracked_handle(
        command,
        context,
    ):
        nonlocal handler_called

        handler_called = True

        return ExecutionResult.success_result(
            message=(
                "Authorization integration test "
                "handler reached."
            ),
            data={
                "purchase_order_id": (
                    command.purchase_order_id
                ),
            },
        )

    handler.handle = tracked_handle

    try:
        dispatcher.dispatch(
            command,
            context,
        )

        assert handler_called is True

    finally:
        handler.handle = original_handle


def test_authorized_expense_submit_reaches_handler(
    app,
    regular_user,
):
    """
    A user with the Expense SUBMIT permission passes the real
    startup execution-authorization path and reaches the
    registered Expense handler.
    """
    dispatcher = app.extensions[
        "command_dispatcher"
    ]

    permission = Permission.query.filter_by(
        name="expense.expense.submit"
    ).first()

    if permission is None:
        permission = Permission(
            name="expense.expense.submit",
            module="EXPENSE",
            description=(
                "Submit Expense Management expense records "
                "for approval."
            ),
        )

        db.session.add(permission)
        db.session.flush()

    if not regular_user.user_roles:
        role = Role(
            name="Expense Execution Authorization Test Role",
            description=(
                "Role used by the Expense execution "
                "authorization integration test."
            ),
            is_system=False,
        )

        db.session.add(role)
        db.session.flush()

        user_role = UserRole(
            user=regular_user,
            role=role,
        )

        db.session.add(user_role)
        db.session.flush()

    else:
        role = regular_user.user_roles[0].role

    existing_role_permission = RolePermission.query.filter_by(
        role_id=role.id,
        permission_id=permission.id,
    ).first()

    if existing_role_permission is None:
        role_permission = RolePermission(
            role=role,
            permission=permission,
        )

        db.session.add(role_permission)

    db.session.commit()

    assert regular_user.has_permission(
        "EXPENSE.EXPENSE.SUBMIT"
    ) is True

    command_name = "expense.submit"

    assert command_registry.exists(
        command_name
    )

    command = SubmitExpenseCommand(
        expense_id=1
    )

    context = ExecutionContext(
        user_id=str(
            regular_user.id
        ),
        module_name="EXPENSE",
        operation="expense.submit",
        metadata={
            "source": "authorization-test",
        },
    )

    handler = dispatcher.get_handler(
        type(command)
    )

    assert handler is not None

    handler_called = False
    original_handle = handler.handle

    def tracked_handle(
        command,
        context,
    ):
        nonlocal handler_called

        handler_called = True

        return ExecutionResult.success_result(
            message=(
                "Expense authorization integration test "
                "handler reached."
            ),
            data={
                "expense_id": (
                    command.expense_id
                ),
            },
        )

    handler.handle = tracked_handle

    try:
        dispatcher.dispatch(
            command,
            context,
        )

        assert handler_called is True

    finally:
        handler.handle = original_handle
