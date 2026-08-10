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

from app.core.execution.authorization_audit import (
    AuthorizationAuditContract,
)

from app.core.execution.authorization_service import (
    ExecutionAuthorizationService,
)

from app.core.execution.authorization_result import (
    AuthorizationResultGovernance,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.results import (
    ExecutionResult,
)


class GovernanceAwareAuthorizationEnforcement:
    """
    Coordinates authorization evaluation with
    execution governance.

    Authorization remains delegated to the existing
    ExecutionAuthorizationService.

    Audit and result governance remain delegated to
    their existing contracts.
    """

    def __init__(
        self,
        authorization_service: ExecutionAuthorizationService,
        audit_contract: AuthorizationAuditContract | None = None,
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

        self.authorization_service = (
            authorization_service
        )

        self.audit_contract = (
            audit_contract
            or AuthorizationAuditContract()
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
        Build the authorization audit event.
        """

        return self.audit_contract.build_event(
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

        if decision.is_allowed():
            return AuthorizationResultGovernance.success_result(
                decision,
                context=context,
                data=data,
                message=message,
                metadata=metadata,
            )

        return AuthorizationResultGovernance.failure_result(
            decision,
            context=context,
            message=message,
            error_code=error_code,
            data=data,
            metadata=metadata,
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

        Returns
        -------
        tuple
            Authorization decision, audit event,
            and governed execution result.
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
