"""
CDCS Enterprise Management Platform (CDCS-EMP)

Execution authorization composition and Procurement
Purchase Request authorization-path tests.
"""

import pytest

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

from app.core.execution.security import (
RegistryBackedPermissionExecutionPolicy,
)

from app.modules.procurement.commands import (
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
    ),

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
