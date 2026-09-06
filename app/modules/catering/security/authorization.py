from __future__ import annotations

from typing import Any, Callable

from app.core.security.exceptions import PermissionDeniedError


AuthorizationEvaluator = Callable[
    [Any, str],
    bool,
]


class CateringAuthorizationAdapter:
    """
    Service-layer authorization adapter for Catering operations.

    Delegates authorization decisions to an injected enterprise
    authorization evaluator without coupling Catering services
    to Flask request context or current_user.
    """

    def __init__(
        self,
        evaluator: AuthorizationEvaluator,
    ) -> None:
        if not callable(evaluator):
            raise ValueError(
                "Authorization evaluator is required."
            )

        self.evaluator = evaluator

    def authorize(
        self,
        subject: Any,
        permission_code: str,
    ) -> bool:
        """
        Evaluate a permission and raise when access is denied.
        """

        if not permission_code:
            raise ValueError(
                "Permission code is required."
            )

        allowed = self.evaluator(
            subject,
            permission_code,
        )

        if not allowed:
            raise PermissionDeniedError(
                permission_code
            )

        return True


__all__ = [
    "AuthorizationEvaluator",
    "CateringAuthorizationAdapter",
]
