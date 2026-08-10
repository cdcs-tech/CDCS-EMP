"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Governance-aware authorization enforcement.
"""

from __future__ import annotations

from typing import Any

from app.core.execution.authorization import (
    AuthorizationDecision,
)

from app.core.execution.authorization_service import (
    ExecutionAuthorizationService,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.governance import (
    ExecutionGovernance,
)

from app.core.execution.results import (
    ExecutionResult,
)


class GovernanceAwareAuthorizationEnforcement:
    """
    Coordinates authorization evaluation with
    execution governance.

    Authorization is delegated to the existing
    ExecutionAuthorizationService.

    Audit and result governance are delegated to
    the existing ExecutionGovernance boundary.
    """

    def __init__(
        self,
        authorization_service: ExecutionAuthorizationService,
        governance: ExecutionGovernance | None = None,
    ) -> None:
        """
        Initialize governance-aware authorization
        enforcement.
        """

        if not isinstance(
            authorization_service,
            ExecutionAuthorizationService,
        ):
            raise TypeError(
                "authorization_service must be an "
                "ExecutionAuthorizationService."
            )

        if governance is not None and not isinstance(
            governance,
            ExecutionGovernance,
        ):
            raise TypeError(
                "governance must be an "
                "ExecutionGovernance."
            )

        self.authorization_service = (
            authorization_service
        )

        self.governance = (
            governance
            or ExecutionGovernance()
        )

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Evaluate authorization through the existing
        authorization service.
        """

        return self.authorization_service.authorize(
            command,
            context,
        )

    def audit_event(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        decision: AuthorizationDecision,
    ):
        """
        Build the authorization audit event through
        the execution governance boundary.
        """

        return self.governance.audit_event(
            command,
            context,
            decision,
        )

    def result(
        self,
        decision: AuthorizationDecision,
        *,
        context: ExecutionContext | None = None,
        data: Any = None,
        message: str = "",
        error_code: str = "AUTHORIZATION_DENIED",
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """
        Convert an authorization decision into a
        governed execution result.
        """

        if not isinstance(
            decision,
            AuthorizationDecision,
        ):
            raise TypeError(
                "decision must be an "
                "AuthorizationDecision."
            )

        return self.governance.governed_result(
            decision,
            context=context,
            data=data,
            message=message,
            error_code=error_code,
            result_metadata=metadata,
        )

    def enforce(
        self,
        command: BaseCommand,
        context: ExecutionContext,
        *,
        data: Any = None,
        message: str = "",
        error_code: str = "AUTHORIZATION_DENIED",
        metadata: dict[str, Any] | None = None,
    ) -> tuple[
        AuthorizationDecision,
        Any,
        ExecutionResult,
    ]:
        """
        Evaluate authorization and produce the
        corresponding audit event and governed
        execution result.
        """

        decision = self.authorize(
            command,
            context,
        )

        event = self.audit_event(
            command,
            context,
            decision,
        )

        result = self.result(
            decision,
            context=context,
            data=data,
            message=message,
            error_code=error_code,
            metadata=metadata,
        )

        return (
            decision,
            event,
            result,
        )


__all__ = [
    "GovernanceAwareAuthorizationEnforcement",
]
