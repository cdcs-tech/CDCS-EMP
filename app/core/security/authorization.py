"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Authorization engine with:
- RBAC permission checks
- Security policy evaluation
- Audit event recording
"""


from app.core.security.roles import Role

from app.core.security.exceptions import (
    PermissionDeniedError,
)

from app.core.security.evaluator import (
    policy_evaluator,
)

from app.core.security.audit import (
    SecurityAuditEvent,
)

from app.core.security.audit_registry import (
    audit_registry,
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



    def _audit(
        self,
        event_type,
        subject,
        permission_code,
        result,
        message="",
    ):
        """
        Create security audit event.
        """

        audit_registry.record(
            SecurityAuditEvent(
                event_type=event_type,
                subject=str(subject),
                resource=permission_code,
                action="authorization",
                result=result,
                message=message,
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
        Authorization check.

        Checks:
        1. Permission
        2. Security policies
        """


        if not self.has_permission(
            subject,
            permission_code,
        ):

            self._audit(
                event_type=
                    "PERMISSION_DENIED",
                subject=subject,
                permission_code=
                    permission_code,
                result="FAILED",
                message=
                    "Permission not granted.",
            )

            return False



        if not self.evaluate_policies(
            policies,
            subject,
            context,
        ):

            self._audit(
                event_type=
                    "POLICY_FAILED",
                subject=subject,
                permission_code=
                    permission_code,
                result="FAILED",
                message=
                    "Security policy failed.",
            )

            return False



        self._audit(
            event_type=
                "PERMISSION_GRANTED",
            subject=subject,
            permission_code=
                permission_code,
            result="SUCCESS",
            message=
                "Authorization successful.",
        )


        return True



    def require_permission(
        self,
        subject,
        permission_code: str,
        policies=None,
        context=None,
    ):
        """
        Validate authorization.
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
