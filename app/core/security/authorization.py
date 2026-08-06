"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Authorization engine with security policy integration.
"""


from app.core.security.roles import Role

from app.core.security.exceptions import (
    PermissionDeniedError,
)

from app.core.security.evaluator import (
    policy_evaluator,
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
        """

        if isinstance(
            subject,
            Role,
        ):

            return subject.has_permission(
                permission_code
            )


        return False



    def evaluate_policies(
        self,
        policies=None,
        subject=None,
        context=None,
    ) -> bool:
        """
        Evaluate security policies.

        Returns True when all policies pass.
        """


        if not policies:

            return True


        results = (
            policy_evaluator.evaluate_all(
                policies,
                subject,
                context,
            )
        )


        return (
            policy_evaluator.all_passed(
                results
            )
        )



    def can(
        self,
        subject,
        permission_code: str,
        policies=None,
        context=None,
    ) -> bool:
        """
        Generic authorization check.

        Checks:
        1. Permission
        2. Security policies
        """


        if not self.has_permission(
            subject,
            permission_code,
        ):

            return False


        return self.evaluate_policies(
            policies,
            subject,
            context,
        )



    def require_permission(
        self,
        subject,
        permission_code: str,
        policies=None,
        context=None,
    ):
        """
        Validate authorization.

        Raises PermissionDeniedError
        when access is denied.
        """


        if not self.can(
            subject,
            permission_code,
            policies,
            context,
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
