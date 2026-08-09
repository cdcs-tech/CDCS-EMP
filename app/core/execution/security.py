"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Security permission registry integration.
"""

from __future__ import annotations

from typing import Any

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
    PermissionExecutionPolicy,
)

from app.core.security.permissions import (
    Permission,
)

from app.core.security.registry import (
    PermissionRegistry,
    permission_registry,
)


class SecurityPermissionResolver:
    """
    Resolves execution permissions against the
    enterprise security PermissionRegistry.

    This class deliberately depends only on the
    existing PermissionRegistry contract.
    """

    def __init__(
        self,
        registry: PermissionRegistry | None = None,
    ) -> None:
        """
        Initialize the security permission resolver.
        """

        self.registry = (
            registry
            or permission_registry
        )

        if not isinstance(
            self.registry,
            PermissionRegistry,
        ):
            raise ExecutionContractException(
                "Security permission resolver requires "
                "a PermissionRegistry."
            )

    def resolve(
        self,
        permission: ExecutionPermission,
    ) -> Permission:
        """
        Resolve an execution permission against
        the security permission registry.
        """

        if not isinstance(
            permission,
            ExecutionPermission,
        ):
            raise ExecutionContractException(
                "Expected an ExecutionPermission."
            )

        registered = self.registry.get(
            permission.code
        )

        if registered is None:
            raise ExecutionContractException(
                f"Security permission "
                f"'{permission.code}' is not "
                "registered."
            )

        if not isinstance(
            registered,
            Permission,
        ):
            raise ExecutionContractException(
                f"Security registry returned an "
                f"invalid permission for "
                f"'{permission.code}'."
            )

        return registered

    def exists(
        self,
        permission_code: str,
    ) -> bool:
        """
        Determine whether a security permission
        exists in the registry.
        """

        if not isinstance(
            permission_code,
            str,
        ) or not permission_code.strip():
            return False

        return self.registry.exists(
            permission_code
        )


class RegistryBackedPermissionExecutionPolicy(
    PermissionExecutionPolicy
):
    """
    Permission execution policy backed by the
    enterprise security PermissionRegistry.

    The policy first resolves the execution
    permission through the security registry.

    The original PermissionExecutionPolicy
    remains available for lightweight or dynamic
    execution scenarios.
    """

    def __init__(
        self,
        registry: PermissionRegistry | None = None,
        permissions: dict[
            str,
            str | ExecutionPermission,
        ] | None = None,
    ) -> None:
        """
        Initialize a registry-backed policy.
        """

        super().__init__(
            permissions=permissions
        )

        self.security_resolver = (
            SecurityPermissionResolver(
                registry
            )
        )

    def resolve_registered_permission(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> Permission | None:
        """
        Resolve the command's configured execution
        permission against the security registry.

        Returns None when the command has no
        permission requirement.
        """

        execution_permission = super().resolve(
            command,
            context,
        )

        if execution_permission is None:
            return None

        return self.security_resolver.resolve(
            execution_permission
        )

    def validate_registered_permissions(
        self,
    ) -> None:
        """
        Validate all configured execution
        permissions against the security registry.
        """

        for command_name in self._permissions:
            configured = self._permissions[
                command_name
            ]

            if isinstance(
                configured,
                str,
            ):
                execution_permission = (
                    ExecutionPermission(
                        code=configured
                    )
                )

            elif isinstance(
                configured,
                ExecutionPermission,
            ):
                execution_permission = configured

            else:
                raise ExecutionContractException(
                    f"Invalid permission configuration "
                    f"for command '{command_name}'."
                )

            self.security_resolver.resolve(
                execution_permission
            )


__all__ = [
    "SecurityPermissionResolver",
    "RegistryBackedPermissionExecutionPolicy",
]
