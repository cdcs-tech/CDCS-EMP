"""
Tests for security permission registry integration.
"""

import pytest

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
)

from app.core.execution.security import (
    RegistryBackedPermissionExecutionPolicy,
    SecurityPermissionResolver,
)

from app.core.security.permissions import (
    Permission,
)

from app.core.security.registry import (
    PermissionRegistry,
)


class TestSecurityCommand(BaseCommand):
    """
    Test command for security integration.
    """

    command_name = "test.security.execute"

    def execute_name(self) -> str:
        return "test.security.execute"


def valid_context() -> ExecutionContext:
    """
    Return a valid execution context.
    """

    return ExecutionContext(
        user_id="test-user",
        module_name="test",
        operation="security_execute",
    )


def create_registry() -> PermissionRegistry:
    """
    Create an isolated permission registry.
    """

    registry = PermissionRegistry()

    registry.register(
        Permission(
            code="test.security.execute",
            name="Execute Security Test",
            description=(
                "Permission for the security "
                "execution test."
            ),
            module="test",
            resource="security",
            action="execute",
        )
    )

    return registry


def test_security_permission_resolver_finds_registered_permission():
    """
    Registered permissions can be resolved.
    """

    registry = create_registry()

    resolver = SecurityPermissionResolver(
        registry
    )

    permission = resolver.resolve(
        ExecutionPermission(
            code="test.security.execute"
        )
    )

    assert isinstance(
        permission,
        Permission,
    )

    assert permission.code == (
        "test.security.execute"
    )


def test_security_permission_resolver_reports_existing_permission():
    """
    The resolver correctly reports existing
    permissions.
    """

    registry = create_registry()

    resolver = SecurityPermissionResolver(
        registry
    )

    assert resolver.exists(
        "test.security.execute"
    )


def test_security_permission_resolver_reports_missing_permission():
    """
    Missing permissions are reported correctly.
    """

    registry = create_registry()

    resolver = SecurityPermissionResolver(
        registry
    )

    assert not resolver.exists(
        "test.security.missing"
    )


def test_security_permission_resolver_rejects_missing_permission():
    """
    Resolving an unregistered permission raises
    an execution contract exception.
    """

    registry = create_registry()

    resolver = SecurityPermissionResolver(
        registry
    )

    with pytest.raises(
        ExecutionContractException
    ):
        resolver.resolve(
            ExecutionPermission(
                code="test.security.missing"
            )
        )


def test_registry_backed_policy_resolves_registered_permission():
    """
    Registry-backed policy resolves a configured
    permission through the security registry.
    """

    registry = create_registry()

    policy = RegistryBackedPermissionExecutionPolicy(
        registry=registry,
        permissions={
            "test.security.execute":
                "test.security.execute"
        },
    )

    permission = (
        policy.resolve_registered_permission(
            TestSecurityCommand(),
            valid_context(),
        )
    )

    assert isinstance(
        permission,
        Permission,
    )

    assert permission.code == (
        "test.security.execute"
    )


def test_registry_backed_policy_rejects_missing_permission():
    """
    Registry-backed policy rejects permissions
    that do not exist in the security registry.
    """

    registry = create_registry()

    policy = RegistryBackedPermissionExecutionPolicy(
        registry=registry,
        permissions={
            "test.security.execute":
                "test.security.missing"
        },
    )

    with pytest.raises(
        ExecutionContractException
    ):
        policy.resolve_registered_permission(
            TestSecurityCommand(),
            valid_context(),
        )


def test_registry_backed_policy_allows_unconfigured_command():
    """
    Commands without a configured permission remain
    compatible with the execution framework.
    """

    registry = create_registry()

    policy = RegistryBackedPermissionExecutionPolicy(
        registry=registry
    )

    permission = (
        policy.resolve_registered_permission(
            TestSecurityCommand(),
            valid_context(),
        )
    )

    assert permission is None


def test_registry_backed_policy_validates_registered_permissions():
    """
    All configured permissions can be validated
    against the security registry.
    """

    registry = create_registry()

    policy = RegistryBackedPermissionExecutionPolicy(
        registry=registry,
        permissions={
            "test.security.execute":
                "test.security.execute"
        },
    )

    policy.validate_registered_permissions()


def test_registry_backed_policy_validation_rejects_missing_permission():
    """
    Permission validation detects missing security
    registry entries.
    """

    registry = create_registry()

    policy = RegistryBackedPermissionExecutionPolicy(
        registry=registry,
        permissions={
            "test.security.execute":
                "test.security.missing"
        },
    )

    with pytest.raises(
        ExecutionContractException
    ):
        policy.validate_registered_permissions()


def test_resolver_uses_supplied_registry():
    """
    The resolver uses the supplied registry rather
    than relying on global registry state.
    """

    registry = PermissionRegistry()

    resolver = SecurityPermissionResolver(
        registry
    )

    assert not resolver.exists(
        "test.security.execute"
    )

    registry.register(
        Permission(
            code="test.security.execute",
            name="Test Execute",
        )
    )

    assert resolver.exists(
        "test.security.execute"
    )
