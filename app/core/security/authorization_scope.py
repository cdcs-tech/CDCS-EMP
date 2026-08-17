"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Authorization Scope Integration.

Provides a scope-aware authorization boundary that combines
RBAC authorization with the authenticated user's active
tenant and organization scope.

This module does not replace the existing AuthorizationEngine.
It provides the integration boundary required to evaluate
authorization within an explicitly resolved organizational scope.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.core.platform.scope import (
    PlatformScopeResolutionException,
    UserScope,
    UserScopeResolver,
)

from app.core.security.authorization import (
    AuthorizationEngine,
)

from app.core.security.exceptions import (
    AuthorizationError,
)


class AuthorizationScopeException(
    AuthorizationError
):
    """
    Base exception for authorization scope failures.
    """


class AuthorizationScopeResolutionException(
    AuthorizationScopeException
):
    """
    Raised when the authorization scope cannot be resolved.
    """


class AuthorizationScopeMismatchException(
    AuthorizationScopeException
):
    """
    Raised when an explicitly supplied scope does not match
    the user's active scope.
    """


@dataclass(frozen=True, slots=True)
class AuthorizationScope:
    """
    Represents the organizational scope used during
    an authorization decision.
    """

    user_id: str

    tenant_id: str

    organization_id: str

    username: str

    def as_context(self) -> dict[str, str]:
        """
        Return the scope in a serialization-friendly form.
        """

        return {
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "organization_id": self.organization_id,
            "username": self.username,
        }


@dataclass(frozen=True, slots=True)
class ScopedAuthorizationDecision:
    """
    Represents an authorization result together with
    the scope under which the decision was evaluated.
    """

    allowed: bool

    permission_code: str

    scope: AuthorizationScope

    reason: str = ""

    metadata: dict[str, Any] | None = None

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


class AuthorizationScopeService:
    """
    Integrates RBAC authorization with the user's active
    tenant and organization scope.

    The service deliberately delegates permission evaluation
    to the existing AuthorizationEngine rather than duplicating
    RBAC logic.
    """

    def __init__(
        self,
        authorization_engine: Optional[
            AuthorizationEngine
        ] = None,
        scope_resolver: type[
            UserScopeResolver
        ] = UserScopeResolver,
    ) -> None:
        """
        Initialize the authorization scope service.
        """

        self.authorization_engine = (
            authorization_engine
            or AuthorizationEngine()
        )

        self.scope_resolver = scope_resolver

    def resolve_scope(
        self,
        user: Any,
    ) -> AuthorizationScope:
        """
        Resolve the user's active organizational scope.
        """

        try:
            resolved = self.scope_resolver.resolve(
                user
            )

        except PlatformScopeResolutionException as exc:
            raise AuthorizationScopeResolutionException(
                str(exc)
            ) from exc

        if resolved is None:
            raise AuthorizationScopeResolutionException(
                "Authorization requires an active "
                "organizational scope."
            )

        return self._from_user_scope(
            resolved
        )

    @staticmethod
    def _from_user_scope(
        scope: UserScope,
    ) -> AuthorizationScope:
        """
        Convert a platform UserScope into the
        authorization-specific scope representation.
        """

        return AuthorizationScope(
            user_id=scope.user_id,
            username=scope.username,
            tenant_id=scope.tenant_id,
            organization_id=scope.organization_id,
        )

    @staticmethod
    def validate_scope(
        scope: AuthorizationScope,
        *,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> None:
        """
        Validate an explicitly supplied scope against the
        user's active scope.

        An omitted value means that dimension is not being
        explicitly constrained.
        """

        if tenant_id is not None:
            if str(tenant_id) != scope.tenant_id:
                raise AuthorizationScopeMismatchException(
                    "Requested tenant scope does not match "
                    "the user's active tenant scope."
                )

        if organization_id is not None:
            if (
                str(organization_id)
                != scope.organization_id
            ):
                raise AuthorizationScopeMismatchException(
                    "Requested organization scope does not "
                    "match the user's active organization scope."
                )

    def authorize(
        self,
        user: Any,
        permission_code: str,
        *,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        policies=None,
        context=None,
    ) -> ScopedAuthorizationDecision:
        """
        Evaluate RBAC authorization within the user's
        active organizational scope.

        The authorization flow is:

        1. Resolve active user scope.
        2. Validate explicitly requested scope.
        3. Delegate RBAC/policy evaluation to AuthorizationEngine.
        4. Return the authorization result together with scope.
        """

        if not permission_code:
            raise AuthorizationScopeException(
                "Permission code is required."
            )

        scope = self.resolve_scope(
            user
        )

        self.validate_scope(
            scope,
            tenant_id=tenant_id,
            organization_id=organization_id,
        )

        authorization_context = (
            self._build_context(
                context,
                scope,
            )
        )

        allowed = self.authorization_engine.can(
            scope.user_id,
            permission_code,
            policies=policies,
            context=authorization_context,
        )

        metadata = {
            "authorization_source": (
                "AuthorizationEngine"
            ),
            "user_id": scope.user_id,
            "tenant_id": scope.tenant_id,
            "organization_id": scope.organization_id,
            "permission_code": permission_code,
        }

        return ScopedAuthorizationDecision(
            allowed=bool(allowed),
            permission_code=permission_code,
            scope=scope,
            reason=(
                "Authorization permitted within "
                "the active organizational scope."
                if allowed
                else
                "Authorization denied within "
                "the active organizational scope."
            ),
            metadata=metadata,
        )

    @staticmethod
    def _build_context(
        context: Any,
        scope: AuthorizationScope,
    ) -> Any:
        """
        Enrich the supplied authorization context with
        the active organizational scope.

        Existing context objects are not mutated.
        """

        scope_metadata = {
            "user_id": scope.user_id,
            "tenant_id": scope.tenant_id,
            "organization_id": scope.organization_id,
        }

        if context is None:
            return scope_metadata

        if hasattr(
            context,
            "with_metadata",
        ):
            return context.with_metadata(
                **scope_metadata
            )

        if isinstance(
            context,
            dict,
        ):
            enriched = dict(context)
            enriched.update(
                scope_metadata
            )
            return enriched

        return context


__all__ = [
    "AuthorizationScopeException",
    "AuthorizationScopeResolutionException",
    "AuthorizationScopeMismatchException",
    "AuthorizationScope",
    "ScopedAuthorizationDecision",
    "AuthorizationScopeService",
]
