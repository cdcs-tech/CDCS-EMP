"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Reporting authorization adapter.
"""

from __future__ import annotations

from typing import Any, Callable

from app.core.reporting.authorization import (
    ReportAuthorizationDecision,
    ReportAuthorizationRequest,
)
from app.core.reporting.permissions import (
    permission_code_for_operation,
)


class ReportingAuthorizationAdapter:
    """
    Adapter between the reporting authorization contract
    and the enterprise security authorization framework.

    The adapter translates a provider-neutral reporting
    authorization request into the canonical enterprise
    permission code and delegates authorization evaluation
    to the supplied evaluator.

    The evaluator must accept:

        request
        permission_code

    and return either:

        bool

    or:

        ReportAuthorizationDecision
    """

    def __init__(
        self,
        evaluator: Callable[
            [ReportAuthorizationRequest, str],
            Any,
        ],
    ) -> None:
        """
        Initialize the reporting authorization adapter.
        """

        if not callable(evaluator):
            raise ValueError(
                "Reporting authorization adapter "
                "requires a callable evaluator."
            )

        self.evaluator = evaluator

    def permission_for(
        self,
        request: ReportAuthorizationRequest,
    ) -> str:
        """
        Resolve the canonical enterprise permission code
        for a reporting authorization request.
        """

        if not isinstance(
            request,
            ReportAuthorizationRequest,
        ):
            raise ValueError(
                "Reporting authorization requires a "
                "ReportAuthorizationRequest."
            )

        return permission_code_for_operation(
            request.operation
        )

    def authorize(
        self,
        request: ReportAuthorizationRequest,
    ) -> ReportAuthorizationDecision:
        """
        Evaluate a reporting authorization request through
        the supplied security evaluator.
        """

        if not isinstance(
            request,
            ReportAuthorizationRequest,
        ):
            raise ValueError(
                "Reporting authorization requires a "
                "ReportAuthorizationRequest."
            )

        permission_code = self.permission_for(
            request
        )

        try:
            result = self.evaluator(
                request,
                permission_code,
            )

        except Exception as exc:
            raise RuntimeError(
                "Reporting authorization evaluation failed."
            ) from exc

        if isinstance(
            result,
            ReportAuthorizationDecision,
        ):
            return result

        if isinstance(
            result,
            bool,
        ):
            if result:
                return ReportAuthorizationDecision(
                    status="allow",
                    reason=(
                        "Reporting authorization "
                        "granted."
                    ),
                    metadata={
                        "permission_code": permission_code,
                    },
                )

            return ReportAuthorizationDecision(
                status="deny",
                reason=(
                    "Reporting authorization "
                    "denied."
                ),
                metadata={
                    "permission_code": permission_code,
                },
            )

        raise RuntimeError(
            "Reporting authorization evaluator must "
            "return a boolean or "
            "ReportAuthorizationDecision."
        )


__all__ = [
    "ReportingAuthorizationAdapter",
]
