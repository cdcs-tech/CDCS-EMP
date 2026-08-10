"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution governance integration contract.
"""

from __future__ import annotations

from typing import Any

from app.core.execution.authorization import (
    AuthorizationDecision,
)

from app.core.execution.authorization_audit import (
    AuthorizationAuditContract,
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


class ExecutionGovernance:
    """
    Coordinates authorization audit and result
    governance for command execution.

    This class provides a stable integration boundary
    between the execution authorization layer and the
    existing audit/result governance components.

    It does not perform authorization itself.
    """

    def __init__(
        self,
        audit_contract: AuthorizationAuditContract | None = None,
    ) -> None:
        """
        Initialize execution governance.
        """

        self.audit_contract = (
            audit_contract
            or AuthorizationAuditContract()
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

    def result_metadata(
        self,
        decision: AuthorizationDecision,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """
        Build governance metadata for an
        authorization decision.
        """

        return AuthorizationResultGovernance.metadata(
            decision,
            context,
        )

    def governed_result(
        self,
        decision: AuthorizationDecision,
        *,
        context: ExecutionContext | None = None,
        data: Any = None,
        message: str = "",
        error_code: str = "AUTHORIZATION_DENIED",
        result_metadata: dict[str, Any] | None = None,
    ):
        metadata = result_metadata or {}

        if context is not None:
            metadata.update(context.metadata)

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


__all__ = [
    "ExecutionGovernance",
]
