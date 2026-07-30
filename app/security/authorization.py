"""
CDCS Enterprise Management Platform (CDCS-EMP)

Authorization Services
"""

from flask_login import current_user


class AuthorizationService:
    """
    Central authorization service.
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
