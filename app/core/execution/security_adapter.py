"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Security framework authorization adapter.
"""

from __future__ import annotations

from typing import Any, Callable

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


class SecurityAuthorizationAdapter(
    ExecutionAuthorizer
):
    """
    Adapter between the CDCS security framework
    and the execution authorization contract.

    The adapter deliberately depends on a supplied
    evaluator callable rather than coupling the
    execution layer directly to a specific security
    evaluator implementation.

    The evaluator must accept:

        command
        context

    and return either:

        bool

    or:

        AuthorizationDecision
    """

    def __init__(
        self,
        evaluator: Callable[
            [BaseCommand, ExecutionContext],
            Any,
        ],
    ) -> None:
        """
        Initialize the security authorization adapter.
        """

        if not callable(evaluator):
            raise ExecutionContractException(
                "Security authorization adapter "
                "requires a callable evaluator."
            )

        self.evaluator = evaluator

    def authorize(
        self,
        command: BaseCommand,
        context: ExecutionContext,
    ) -> AuthorizationDecision:
        """
        Evaluate command authorization through
        the supplied security evaluator.
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
            decision = self.evaluator(
                command,
                context,
            )

        except Exception as exc:
            raise ExecutionContractException(
                "Security authorization evaluation "
                "failed."
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
                        "Execution permitted by "
                        "the security framework."
                    )
                )

            return AuthorizationDecision.deny(
                reason=(
                    "Execution denied by "
                    "the security framework."
                )
            )

        raise ExecutionContractException(
            "Security evaluator must return "
            "a boolean or AuthorizationDecision."
        )


__all__ = [
    "SecurityAuthorizationAdapter",
]
