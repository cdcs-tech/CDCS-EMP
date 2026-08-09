"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Permission-aware execution policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

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


@dataclass(frozen=True)
class ExecutionPermission:
    """
    Describes a permission requirement for a command.
    """

    code: str

    description: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate the permission definition.
        """

        if not isinstance(
            self.code,
            str,
        ) or not self.code.strip():
            raise ExecutionContractException(
                "Execution permission requires "
                "a non-empty permission code."
            )


class PermissionExecutionPolicy:
    """
    Resolves permission requirements for commands.

    The policy itself does not evaluate users or roles.

    Instead, it resolves:

        command -> permission

    and delegates the actual security decision to
    the supplied evaluator.
    """

    def __init__(
        self,
        permissions: Mapping[
            str,
            str | ExecutionPermission,
        ] | None = None,
        *,
        resolver: Callable[
            [BaseCommand, ExecutionContext],
            str | ExecutionPermission | None,
        ] | None = None,
    ) -> None:
        """
        Initialize the permission execution policy.

        Parameters
        ----------
        permissions:
            Mapping of command names to permission codes
            or ExecutionPermission objects.

        resolver:
            Optional dynamic permission resolver.
        """

        self._permissions = dict(
            permissions or {}
        )

        if resolver is not None and not callable(
            resolver
        ):
            raise ExecutionContractException(
                "Permission resolver must be callable."
            )

        self._resolver = resolver

    def register(
        self,
        command_name: str,
        permission: str | ExecutionPermission,
    ) -> None:
        """
        Register a permission requirement for a command.
        """

        if not isinstance(
            command_name,
            str,
        ) or not command_name.strip():
            raise ExecutionContractException(
                "Command name is required."
            )

        if isinstance(
            permission,
            str,
        ):
            permission = ExecutionPermission(
                code=permission
            )

        if not isinstance(
            permission,
            ExecutionPermission,
        ):
            raise ExecutionContractException(
                "Permission must be a permission "
                "code or ExecutionPermission."
            )

        self._permissions[
            command_name
        ] = permission

    def unregister(
        self,
        command_name: str,
    ) -> ExecutionPermission | str | None:
        """
        Remove a command permission requirement.
        """

        return self._permissions.pop(
            command_name,
            None,
        )

    def has_permission_requirement(
        self,
        command_name: str,
    ) -> bool:
        """
        Determine whether a command has a
        configured permission requirement.
        """

        return command_name in self._permissions

    def resolve(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> ExecutionPermission | None:
        """
        Resolve the permission required by a command.
        """

        if not isinstance(
            command,
            BaseCommand,
        ):
            raise ExecutionContractException(
                "Permission resolution requires "
                "a BaseCommand."
            )

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise ExecutionContractException(
                "Permission resolution requires "
                "an ExecutionContext."
            )

        if self._resolver is not None:
            resolved = self._resolver(
                command,
                context,
            )

            if resolved is None:
                return None

            if isinstance(
                resolved,
                str,
            ):
                return ExecutionPermission(
                    code=resolved
                )

            if isinstance(
                resolved,
                ExecutionPermission,
            ):
                return resolved

            raise ExecutionContractException(
                "Permission resolver must return "
                "a permission code, ExecutionPermission, "
                "or None."
            )

        configured = self._permissions.get(
            command.command_name
        )

        if configured is None:
            return None

        if isinstance(
            configured,
            str,
        ):
            return ExecutionPermission(
                code=configured
            )

        if isinstance(
            configured,
            ExecutionPermission,
        ):
            return configured

        raise ExecutionContractException(
            "Configured permission must be a "
            "permission code or ExecutionPermission."
        )


class PermissionAwareExecutionAuthorizer(
    ExecutionAuthorizer
):
    """
    Execution authorizer that applies a
    permission-aware execution policy.

    The supplied evaluator is responsible for the
    actual security decision.

    Supported evaluator results:

        bool

        AuthorizationDecision
    """

    def __init__(
        self,
        policy: PermissionExecutionPolicy,
        evaluator: Callable[
            [
                BaseCommand,
                ExecutionContext,
                ExecutionPermission,
            ],
            Any,
        ],
    ) -> None:
        """
        Initialize the permission-aware authorizer.
        """

        if not isinstance(
            policy,
            PermissionExecutionPolicy,
        ):
            raise ExecutionContractException(
                "Permission-aware authorizer requires "
                "a PermissionExecutionPolicy."
            )

        if not callable(
            evaluator
        ):
            raise ExecutionContractException(
                "Permission evaluator must be callable."
            )

        self.policy = policy
        self.evaluator = evaluator

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Evaluate the permission required for a command.
        """

        if not isinstance(
            command,
            BaseCommand,
        ):
            raise ExecutionContractException(
                "Authorization requires a BaseCommand."
            )

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise ExecutionContractException(
                "Authorization requires an "
                "ExecutionContext."
            )

        try:
            permission = self.policy.resolve(
                command,
                context,
            )
        except ExecutionContractException:
            raise
        except Exception as exc:
            raise ExecutionContractException(
                "Permission resolution failed."
            ) from exc

        # No permission requirement means that
        # the command remains compatible with the
        # existing execution framework.
        if permission is None:
            return AuthorizationDecision.allow(
                reason=(
                    "No permission requirement is "
                    "configured for this command."
                )
            )

        try:
            decision = self.evaluator(
                command,
                context,
                permission,
            )

        except Exception as exc:
            raise ExecutionContractException(
                "Permission evaluation failed."
            ) from exc

        if isinstance(
            decision,
            AuthorizationDecision,
        ):
            return decision

        if isinstance(
            decision,
            bool,
        ):
            if decision:
                return AuthorizationDecision.allow(
                    reason=(
                        f"Permission '{permission.code}' "
                        "was granted."
                    ),
                    metadata={
                        "permission": permission.code,
                    },
                )

            return AuthorizationDecision.deny(
                reason=(
                    f"Permission '{permission.code}' "
                    "was denied."
                ),
                metadata={
                    "permission": permission.code,
                },
            )

        raise ExecutionContractException(
            "Permission evaluator must return "
            "a boolean or AuthorizationDecision."
        )


__all__ = [
    "ExecutionPermission",
    "PermissionExecutionPolicy",
    "PermissionAwareExecutionAuthorizer",
]
