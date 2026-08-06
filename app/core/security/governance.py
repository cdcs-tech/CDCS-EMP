"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security governance manager.
"""

from app.core.security.registry import (
    permission_registry,
)

from app.core.security.role_registry import (
    role_registry,
)

from app.core.security.policy_registry import (
    policy_registry,
)

from app.core.security.audit_registry import (
    audit_registry,
)

from app.core.security.authorization import (
    authorization_engine,
)

from app.core.security.compliance_registry import (
    compliance_registry,
)


class SecurityGovernanceManager:
    """
    Central access point for the enterprise
    security governance framework.
    """

    def __init__(self):
        """
        Initialize governance manager.
        """

        self.permissions = permission_registry
        self.roles = role_registry
        self.policies = policy_registry
        self.audit = audit_registry
        self.compliance = compliance_registry
        self.authorization = authorization_engine

    def summary(self):
        """
        Return governance summary.
        """

        return {
            "permissions": self.permissions.count(),
            "roles": self.roles.count(),
            "policies": self.policies.count(),
            "compliance_controls": self.compliance.count(),
            "audit_events": self.audit.count(),

        }

    def clear_audit(self):
        """
        Clear audit events.
        """

        self.audit.clear()

    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            "<SecurityGovernanceManager>"
        )


# Global governance manager

security_governance = SecurityGovernanceManager()
