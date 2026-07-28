"""
Authorization Services
"""

from flask_login import current_user


class AuthorizationService:
    """
    Handles permission evaluation.
    """

    @staticmethod
    def has_permission(permission):

        if not current_user.is_authenticated:
            return False

        return current_user.has_permission(
            permission
        )


    @staticmethod
    def has_role(role):

        if not current_user.is_authenticated:
            return False

        return current_user.has_role(
            role
        )
