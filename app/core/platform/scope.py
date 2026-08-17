"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

User Scope Resolution.

Provides a standardized mechanism for resolving the
authenticated user's active tenant and organization
scope without coupling authentication to execution
context management.
"""

from dataclasses import dataclass
from typing import Optional

from app.models import User


class PlatformScopeException(
    Exception
):
    """
    Base exception for platform scope errors.
    """


class PlatformScopeResolutionException(
    PlatformScopeException
):
    """
    Raised when a user's organizational scope
    cannot be resolved.
    """


class PlatformScopeAmbiguityException(
    PlatformScopeResolutionException
):
    """
    Raised when a user has multiple active
    organization memberships and no explicit
    organization has been selected.
    """


@dataclass(frozen=True, slots=True)
class UserScope:
    """
    Represents the resolved organizational scope
    of a platform user.
    """

    user_id: str

    username: str

    tenant_id: str

    organization_id: str


class UserScopeResolver:
    """
    Resolve the active tenant and organization scope
    for a platform user.
    """

    @staticmethod
    def resolve(
        user: Optional[User],
    ) -> Optional[UserScope]:
        """
        Resolve the active scope for a user.

        Returns None when no user is supplied.

        Raises:
            PlatformScopeResolutionException:
                When the user's active scope cannot be
                resolved.

            PlatformScopeAmbiguityException:
                When multiple active organization
                memberships exist.
        """

        if user is None:
            return None

        if not user.is_active:
            raise PlatformScopeResolutionException(
                "User is inactive."
            )

        if user.is_deleted:
            raise PlatformScopeResolutionException(
                "User is deleted."
            )

        memberships = [
            membership
            for membership
            in user.organization_memberships
            if membership.is_active
        ]

        if not memberships:
            raise PlatformScopeResolutionException(
                "User has no active organization membership."
            )

        if len(memberships) > 1:
            raise PlatformScopeAmbiguityException(
                "User has multiple active organization "
                "memberships. An explicit organization "
                "selection is required."
            )

        membership = memberships[0]

        organization = (
            membership.organization
        )

        if organization is None:
            raise PlatformScopeResolutionException(
                "Active organization membership has no "
                "associated organization."
            )

        if not organization.is_active:
            raise PlatformScopeResolutionException(
                "Organization is inactive."
            )

        tenant = organization.tenant

        if tenant is None:
            raise PlatformScopeResolutionException(
                "Organization has no associated tenant."
            )

        if not tenant.is_active:
            raise PlatformScopeResolutionException(
                "Tenant is inactive."
            )

        if user.id is None:
            raise PlatformScopeResolutionException(
                "User ID is required for scope resolution."
            )

        if organization.id is None:
            raise PlatformScopeResolutionException(
                "Organization ID is required for scope resolution."
            )

        if tenant.id is None:
            raise PlatformScopeResolutionException(
                "Tenant ID is required for scope resolution."
            )

        return UserScope(
            user_id=str(user.id),
            username=user.username,
            tenant_id=str(tenant.id),
            organization_id=str(
                organization.id
            ),
        )

    @staticmethod
    def resolve_authenticated():
        """
        Resolve the scope of the currently authenticated
        Flask-Login user.

        Returns None when no user is authenticated.
        """

        from flask_login import current_user

        if not current_user.is_authenticated:
            return None

        return UserScopeResolver.resolve(
            current_user
        )


__all__ = [
    "PlatformScopeException",
    "PlatformScopeResolutionException",
    "PlatformScopeAmbiguityException",
    "UserScope",
    "UserScopeResolver",
]
