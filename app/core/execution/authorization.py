"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution authorization contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class AuthorizationDecision:
    """
    Represents the result of an authorization decision.
    """

    def __init__(
        self,
        allowed: bool,
        *,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:

        self.allowed = bool(
            allowed
        )

        self.reason = reason

        self.metadata = dict(
            metadata or {}
        )

    @classmethod
    def allow(
        cls,
        *,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "AuthorizationDecision":
        """
        Create an allowed authorization decision.
        """

        return cls(
            True,
            reason=reason,
            metadata=metadata,
        )

    @classmethod
    def deny(
        cls,
        *,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "AuthorizationDecision":
        """
        Create a denied authorization decision.
        """

        return cls(
            False,
            reason=reason,
            metadata=metadata,
        )

    def is_allowed(self) -> bool:
        """
        Determine whether authorization was granted.
        """

        return self.allowed

    def is_denied(self) -> bool:
        """
        Determine whether authorization was denied.
        """

        return not self.allowed


class ExecutionAuthorizer(ABC):
    """
    Base authorization contract for command execution.

    Implementations determine whether a command may
    execute within the supplied execution context.
    """

    @abstractmethod
    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Evaluate authorization for a command.
        """

        raise NotImplementedError


class AllowAllExecutionAuthorizer(
    ExecutionAuthorizer
):
    """
    Default compatibility authorization implementation.

    This implementation preserves the existing execution
    behavior while enterprise authorization is enabled.
    """

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Allow a valid execution request.
        """

        if not isinstance(
            command,
            BaseCommand,
        ):
            raise ExecutionContractException(
                "Authorization requires a "
                "BaseCommand."
            )

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise ExecutionContractException(
                "Authorization requires an "
                "ExecutionContext."
            )

        return AuthorizationDecision.allow(
            reason=(
                "Execution permitted by the "
                "default authorization policy."
            )
        )


class RoleAssignmentExecutionAuthorizer(
    ExecutionAuthorizer
):
    """
    Role/assignment-aware execution authorizer.

    Delegates role, permission assignment, and policy
    evaluation to the existing enterprise
    AuthorizationEngine.
    """

    def __init__(
        self,
        authorization_engine: Any,
    ) -> None:
        """
        Initialize the role/assignment-aware authorizer.
        """

        if authorization_engine is None:
            raise ExecutionContractException(
                "Authorization engine is required."
            )

        can_method = getattr(
            authorization_engine,
            "can",
            None,
        )

        if not callable(
            can_method
        ):
            raise ExecutionContractException(
                "Authorization engine must "
                "provide a callable 'can' method."
            )

        self.authorization_engine = (
            authorization_engine
        )

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Evaluate command authorization using the
        existing enterprise AuthorizationEngine.
        """

        if not isinstance(
            command,
            BaseCommand,
        ):
            raise ExecutionContractException(
                "Authorization requires a "
                "BaseCommand."
            )

        if not isinstance(
            context,
            ExecutionContext,
        ):
            raise ExecutionContractException(
                "Authorization requires an "
                "ExecutionContext."
            )

        if not context.user_id:
            return AuthorizationDecision.deny(
                reason=(
                    "Execution authorization "
                    "requires a user identity."
                )
            )

        permission_code = (
            getattr(
                command,
                "permission_code",
                None,
            )
            or getattr(
                command,
                "required_permission",
                None,
            )
        )

        if not permission_code:
            return AuthorizationDecision.deny(
                reason=(
                    "Command does not define a "
                    "required permission."
                )
            )

        try:
            allowed = self.authorization_engine.can(
                context.user_id,
                permission_code,
                context=context,
            )

        except Exception as exc:
            raise ExecutionContractException(
                "Enterprise authorization "
                "evaluation failed."
            ) from exc

        if bool(allowed):
            return AuthorizationDecision.allow(
                reason=(
                    "Execution authorized through "
                    "role and permission assignment."
                ),
                metadata={
                    "user_id": context.user_id,
                    "permission_code": permission_code,
                    "authorization_source": (
                        "AuthorizationEngine"
                    ),
                },
            )

        return AuthorizationDecision.deny(
            reason=(
                "User is not authorized for "
                "the required permission."
            ),
            metadata={
                "user_id": context.user_id,
                "permission_code": permission_code,
                "authorization_source": (
                    "AuthorizationEngine"
                ),
            },
        )


def validate_authorization_contract(
    command: BaseCommand,
    context: ExecutionContext,
    authorizer: ExecutionAuthorizer,
) -> None:
    """
    Validate the execution authorization contract.
    """

    if not isinstance(
        command,
        BaseCommand,
    ):
        raise ExecutionContractException(
            "Authorization requires a "
            "BaseCommand."
        )

    if not isinstance(
        context,
        ExecutionContext,
    ):
        raise ExecutionContractException(
            "Authorization requires an "
            "ExecutionContext."
        )

    if not isinstance(
        authorizer,
        ExecutionAuthorizer,
    ):
        raise ExecutionContractException(
            "Authorizer must implement "
            "ExecutionAuthorizer."
        )


__all__ = [
    "AuthorizationDecision",
    "ExecutionAuthorizer",
    "AllowAllExecutionAuthorizer",
    "RoleAssignmentExecutionAuthorizer",
    "validate_authorization_contract",
]
