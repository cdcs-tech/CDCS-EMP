"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Authorization engine.
"""


from app.core.security.roles import Role

from app.core.security.exceptions import (
    PermissionDeniedError,
)



class AuthorizationEngine:
    """
    Enterprise authorization decision engine.
    """



    def has_permission(
        self,
        subject,
        permission_code: str,
    ) -> bool:
        """
        Check whether subject has permission.

        Subject currently supports:
        - Role objects

        Future:
        - User objects
        - Groups
        - Delegations
        """


        if isinstance(
            subject,
            Role,
        ):

            return subject.has_permission(
                permission_code
            )


        return False



    def can(
        self,
        subject,
        permission_code: str,
    ) -> bool:
        """
        Generic authorization check.
        """

        return self.has_permission(
            subject,
            permission_code,
        )



    def require_permission(
        self,
        subject,
        permission_code: str,
    ):
        """
        Validate permission.

        Raises PermissionDeniedError
        when access is denied.
        """


        if not self.has_permission(
            subject,
            permission_code,
        ):

            raise PermissionDeniedError(
                permission_code
            )


        return True



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            "<AuthorizationEngine>"
        )



# Global authorization engine

authorization_engine = AuthorizationEngine()
