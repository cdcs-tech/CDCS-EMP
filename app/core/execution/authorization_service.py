"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution authorization service.
"""

from __future__ import annotations

from typing import Any

from app.core.execution.authorization import (
    AuthorizationDecision,
    ExecutionAuthorizer,
    validate_authorization_contract,
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


class ExecutionAuthorizationService:
    """
    Application-level authorization service.

    Provides the execution layer with a stable authorization
    boundary while delegating the actual security evaluation
    to an ExecutionAuthorizer implementation.
    """

    def __init__(
        self,
        authorizer: ExecutionAuthorizer,
    ) -> None:
        """
        Initialize the authorization service.
        """

        if not isinstance(
            authorizer,
            ExecutionAuthorizer,
        ):
            raise ExecutionContractException(
                "Authorization service requires "
                "an ExecutionAuthorizer."
            )

        self.authorizer = authorizer

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Authorize a command for execution.
        """

        validate_authorization_contract(
            command,
            context,
            self.authorizer,
        )

        decision = self.authorizer.authorize(
            command,
            context,
        )

        if not isinstance(
            decision,
            AuthorizationDecision,
        ):
            raise ExecutionContractException(
                "Authorization provider returned "
                "an invalid authorization decision."
            )

        return decision

    def is_allowed(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> bool:
        """
        Determine whether command execution is allowed.
        """

        return self.authorize(
            command,
            context,
        ).is_allowed()

    def require_authorization(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Require authorization for command execution.

        Raises ExecutionContractException when the
        authorization decision denies execution.
        """

        decision = self.authorize(
            command,
            context,
        )

        if decision.is_denied():
            raise ExecutionContractException(
                decision.reason
                or "Command execution is not authorized."
            )

        return decision

    def metadata(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """
        Return authorization metadata.

        The returned dictionary is a copy and can therefore
        be safely enriched by callers.
        """

        decision = self.authorize(
            command,
            context,
        )

        return dict(
            decision.metadata
        )


__all__ = [
    "ExecutionAuthorizationService",
]
