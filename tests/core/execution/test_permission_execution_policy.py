"""
Tests for permission-aware execution policy.
"""

import pytest

from app.core.execution.authorization import (
    AuthorizationDecision,
    ExecutionAuthorizer,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)

from app.core.execution.policy import (
    ExecutionPermission,
    PermissionAwareExecutionAuthorizer,
    PermissionExecutionPolicy,
)


class TestCommand(BaseCommand):
    """
    Test command.
    """

    command_name = "test.permission.execute"

    def execute_name(self) -> str:
        return "test.permission.execute"


def valid_context() -> ExecutionContext:
    """
    Create a valid execution context.
    """

    return ExecutionContext(
        user_id="test-user",
        module_name="test",
        operation="permission_execute",
    )


def test_execution_permission_requires_code():
    """
    Permission definitions require a code.
    """

    with pytest.raises(
        ExecutionContractException
    ):
        ExecutionPermission(
            code=""
        )


def test_execution_permission_can_be_created():
    """
    Valid permission definitions are accepted.
    """

    permission = ExecutionPermission(
        code="test.execute",
        description="Execute test operation.",
    )

    assert permission.code == (
        "test.execute"
    )


def test_policy_registers_permission():
    """
    A command can be mapped to a permission.
    """

    policy = PermissionExecutionPolicy()

    policy.register(
        "test.permission.execute",
        "test.execute",
    )

    assert policy.has_permission_requirement(
        "test.permission.execute"
    )

    permission = policy.resolve(
        TestCommand(),
        valid_context(),
    )

    assert permission is not None
    assert permission.code == (
        "test.execute"
    )


def test_policy_supports_execution_permission():
    """
    The policy accepts ExecutionPermission objects.
    """

    policy = PermissionExecutionPolicy()

    policy.register(
        "test.permission.execute",
        ExecutionPermission(
            code="test.execute",
            description="Test permission.",
        ),
    )

    permission = policy.resolve(
        TestCommand(),
        valid_context(),
    )

    assert permission is not None
    assert permission.code == (
        "test.execute"
    )


def test_policy_returns_none_for_unconfigured_command():
    """
    Commands without a configured permission remain
    compatible with the execution framework.
    """

    policy = PermissionExecutionPolicy()

    permission = policy.resolve(
        TestCommand(),
        valid_context(),
    )

    assert permission is None


def test_policy_supports_dynamic_resolver():
    """
    The policy can resolve permissions dynamically.
    """

    policy = PermissionExecutionPolicy(
        resolver=lambda command, context: (
            "test.dynamic.execute"
        )
    )

    permission = policy.resolve(
        TestCommand(),
        valid_context(),
    )

    assert permission is not None
    assert permission.code == (
        "test.dynamic.execute"
    )


def test_permission_authorizer_allows_permission():
    """
    A granted permission produces an allow decision.
    """

    policy = PermissionExecutionPolicy(
        permissions={
            "test.permission.execute":
                "test.execute"
        }
    )

    authorizer = (
        PermissionAwareExecutionAuthorizer(
            policy,
            lambda command, context, permission: True,
        )
    )

    decision = authorizer.authorize(
        TestCommand(),
        valid_context(),
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_allowed()
    assert decision.metadata[
        "permission"
    ] == "test.execute"


def test_permission_authorizer_denies_permission():
    """
    A denied permission produces a deny decision.
    """

    policy = PermissionExecutionPolicy(
        permissions={
            "test.permission.execute":
                "test.execute"
        }
    )

    authorizer = (
        PermissionAwareExecutionAuthorizer(
            policy,
            lambda command, context, permission: False,
        )
    )

    decision = authorizer.authorize(
        TestCommand(),
        valid_context(),
    )

    assert decision.is_denied()
    assert decision.metadata[
        "permission"
    ] == "test.execute"


def test_permission_authorizer_allows_unconfigured_command():
    """
    An unconfigured command remains allowed.
    """

    policy = PermissionExecutionPolicy()

    authorizer = (
        PermissionAwareExecutionAuthorizer(
            policy,
            lambda command, context, permission: (
                pytest.fail(
                    "Evaluator should not be called."
                )
            ),
        )
    )

    decision = authorizer.authorize(
        TestCommand(),
        valid_context(),
    )

    assert decision.is_allowed()


def test_permission_authorizer_preserves_decision():
    """
    AuthorizationDecision results are preserved.
    """

    expected = AuthorizationDecision.deny(
        reason="Security policy denied.",
        metadata={
            "source": "test"
        },
    )

    policy = PermissionExecutionPolicy(
        permissions={
            "test.permission.execute":
                "test.execute"
        }
    )

    authorizer = (
        PermissionAwareExecutionAuthorizer(
            policy,
            lambda command, context, permission: expected,
        )
    )

    decision = authorizer.authorize(
        TestCommand(),
        valid_context(),
    )

    assert decision is expected


def test_permission_authorizer_requires_policy():
    """
    The authorizer requires a valid policy.
    """

    with pytest.raises(
        ExecutionContractException
    ):
        PermissionAwareExecutionAuthorizer(
            object(),
            lambda command, context, permission: True,
        )


def test_permission_authorizer_requires_evaluator():
    """
    The authorizer requires a callable evaluator.
    """

    policy = PermissionExecutionPolicy()

    with pytest.raises(
        ExecutionContractException
    ):
        PermissionAwareExecutionAuthorizer(
            policy,
            object(),
        )


def test_permission_evaluator_invalid_result_is_rejected():
    """
    Unsupported evaluator results are rejected.
    """

    policy = PermissionExecutionPolicy(
        permissions={
            "test.permission.execute":
                "test.execute"
        }
    )

    authorizer = (
        PermissionAwareExecutionAuthorizer(
            policy,
            lambda command, context, permission: (
                "allowed"
            ),
        )
    )

    with pytest.raises(
        ExecutionContractException
    ):
        authorizer.authorize(
            TestCommand(),
            valid_context(),
        )


def test_permission_evaluator_failure_is_wrapped():
    """
    Evaluator failures are converted to execution
    contract exceptions.
    """

    policy = PermissionExecutionPolicy(
        permissions={
            "test.permission.execute":
                "test.execute"
        }
    )

    def broken_evaluator(
        command,
        context,
        permission,
    ):
        raise RuntimeError(
            "Security failure."
        )

    authorizer = (
        PermissionAwareExecutionAuthorizer(
            policy,
            broken_evaluator,
        )
    )

    with pytest.raises(
        ExecutionContractException
    ) as exc_info:

        authorizer.authorize(
            TestCommand(),
            valid_context(),
        )

    assert (
        "Permission evaluation failed."
        in str(exc_info.value)
    )
