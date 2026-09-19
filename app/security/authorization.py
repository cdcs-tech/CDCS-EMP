"""
CDCS Enterprise Management Platform (CDCS-EMP)

Authorization Services
"""

from __future__ import annotations

from flask_login import current_user

from app.core.security.authorization import authorization_engine
from app.core.security.permissions import Permission
from app.core.security.roles import Role
from app.models import User


class AuthorizationService:
    """
    Central application authorization service.

    This service owns the application-to-enterprise authorization
    integration boundary while delegating authorization evaluation
    to the existing enterprise authorization engine.
    """

    @staticmethod
    def is_authenticated():
        return current_user.is_authenticated

    @staticmethod
    def has_role(role):
        if not current_user.is_authenticated:
            return False

        return current_user.has_role(role)

    @staticmethod
    def has_permission(permission):
        if not current_user.is_authenticated:
            return False

        return current_user.has_permission(permission)

    @staticmethod
    def has_permissions(*permissions):
        if not current_user.is_authenticated:
            return False

        return all(
            current_user.has_permission(permission)
            for permission in permissions
        )

    @staticmethod
    def authorize_execution(
        user_id,
        permission_code: str,
        *,
        context=None,
    ) -> bool:
        """
        Evaluate an execution permission for an application user.

        The application persistence RBAC model remains responsible for
        resolving whether the user possesses the requested permission.
        The result is then represented using enterprise Role/Permission
        objects and evaluated by the existing enterprise authorization
        engine.

        The enterprise security layer therefore remains independent of
        application persistence models.
        """

        if user_id is None:
            return False

        if not isinstance(permission_code, str):
            return False

        normalized_permission = permission_code.strip()

        if not normalized_permission:
            return False

        user = User.query.get(user_id)

        if user is None:
            return False

        if not user.is_active:
            return False

        if not user.has_permission(normalized_permission):
            return False

        permission = Permission(
            code=normalized_permission.upper(),
            name=normalized_permission.lower(),
            description="Application execution permission.",
        )

        subject = Role(
            code=f"APPLICATION_USER_{user.id}",
            name=f"Application User {user.id}",
            description="Application user execution authorization subject.",
        )

        subject.add_permission(permission)

        return authorization_engine.can(
            subject,
            permission.code,
            context=context,
        )


__all__ = ["AuthorizationService"]
