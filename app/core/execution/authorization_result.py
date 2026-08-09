"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Authorization result governance.
"""

from __future__ import annotations

from typing import Any

from app.core.execution.authorization import (
    AuthorizationDecision,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.results import (
    ExecutionResult,
)


class AuthorizationResultGovernance:
    """
    Provides a stable boundary for translating an
    authorization decision into execution-result
    governance metadata.
    """

    @staticmethod
    def metadata(
        decision: AuthorizationDecision,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        """
        Build governance metadata from an authorization
        decision and optional execution context.
        """

        if not isinstance(
            decision,
            AuthorizationDecision,
        ):
            raise TypeError(
                "decision must be an "
                "AuthorizationDecision."
            )

        if context is not None and not isinstance(
            context,
            ExecutionContext,
        ):
            raise TypeError(
                "context must be an "
                "ExecutionContext."
            )

        metadata: dict[str, Any] = {
            "authorization_allowed": (
                decision.is_allowed()
            ),
            "authorization_reason": (
                decision.reason
            ),
            "authorization_metadata": dict(
                decision.metadata
            ),
        }

        if context is not None:
            metadata.update(
                {
                    "user_id": context.user_id,
                    "module_name": context.module_name,
                    "operation": context.operation,
                    "request_id": context.request_id,
                    "correlation_id": (
                        context.correlation_id
                    ),
                    "trace_id": context.trace_id,
                }
            )

        return metadata

    @classmethod
    def success_result(
        cls,
        decision: AuthorizationDecision,
        *,
        context: ExecutionContext | None = None,
        data: Any = None,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """
        Build a successful execution result governed
        by an allowed authorization decision.
        """

        if not decision.is_allowed():
            raise ValueError(
                "A denied authorization decision "
                "cannot produce a success result."
            )

        result_metadata = cls.metadata(
            decision,
            context,
        )

        result_metadata.update(
            metadata or {}
        )

        return ExecutionResult.success_result(
            data=data,
            message=message,
            metadata=result_metadata,
        )

    @classmethod
    def failure_result(
        cls,
        decision: AuthorizationDecision,
        *,
        context: ExecutionContext | None = None,
        message: str = "",
        error_code: str = (
            "AUTHORIZATION_DENIED"
        ),
        data: Any = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionResult:
        """
        Build a failed execution result governed
        by an authorization decision.
        """

        if decision.is_allowed():
            raise ValueError(
                "An allowed authorization decision "
                "cannot produce an authorization "
                "failure result."
            )

        result_metadata = cls.metadata(
            decision,
            context,
        )

        result_metadata.update(
            metadata or {}
        )

        return ExecutionResult.failure_result(
            message=(
                message
                or decision.reason
                or "Command execution was "
                "not authorized."
            ),
            error_code=error_code,
            data=data,
            metadata=result_metadata,
        )


__all__ = [
    "AuthorizationResultGovernance",
]
