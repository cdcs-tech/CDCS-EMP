"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Public security framework interface.
"""


# ---------------------------------------------------------
# Security Exceptions
# ---------------------------------------------------------

from app.core.security.exceptions import (
    SecurityException,
    AuthenticationError,
    AuthorizationError,
    PermissionDeniedError,
    SecurityPolicyViolationError,
)


# ---------------------------------------------------------
# Permission Framework
# ---------------------------------------------------------

from app.core.security.permissions import (
    Permission,
)


from app.core.security.registry import (
    PermissionRegistry,
    permission_registry,
)


# ---------------------------------------------------------
# Module Security
# ---------------------------------------------------------

from app.core.security.module import (
    ModulePermission,
)


# ---------------------------------------------------------
# RBAC Framework
# ---------------------------------------------------------

from app.core.security.roles import (
    Role,
)


from app.core.security.role_registry import (
    RoleRegistry,
    role_registry,
)


from app.core.security.assignment import (
    RolePermissionAssignment,
)


from app.core.security.authorization import (
    AuthorizationEngine,
    authorization_engine,
)


# ---------------------------------------------------------
# Security Policy Framework
# ---------------------------------------------------------

from app.core.security.policies import (
    SecurityPolicy,
)


from app.core.security.policy_registry import (
    PolicyRegistry,
    policy_registry,
)


from app.core.security.evaluator import (
    PolicyEvaluationResult,
    PolicyEvaluator,
    policy_evaluator,
)


# ---------------------------------------------------------
# Security Audit Framework
# ---------------------------------------------------------

from app.core.security.audit import (
    SecurityAuditEvent,
)

from app.core.security.audit_registry import (
    AuditRegistry,
    audit_registry,
)

# ---------------------------------------------------------
# Security Compliance Framework
# ---------------------------------------------------------

from app.core.security.compliance import (
    ComplianceControl,
)


# ---------------------------------------------------------
# Compliance Registry
# ---------------------------------------------------------

from app.core.security.compliance_registry import (
    ComplianceRegistry,
    compliance_registry,
)

# ---------------------------------------------------------
# Security Governance
# ---------------------------------------------------------

from app.core.security.governance import (
    SecurityGovernanceManager,
    security_governance,
)


__all__ = [

    # Security Exceptions

    "SecurityException",

    "AuthenticationError",

    "AuthorizationError",

    "PermissionDeniedError",

    "SecurityPolicyViolationError",


    # Permission Framework

    "Permission",

    "PermissionRegistry",

    "permission_registry",


    # Module Security

    "ModulePermission",


    # RBAC Framework

    "Role",

    "RoleRegistry",

    "role_registry",

    "RolePermissionAssignment",

    "AuthorizationEngine",

    "authorization_engine",

    # Security Policy Framework

    "SecurityPolicy",

    "PolicyRegistry",

    "policy_registry",

    "PolicyEvaluationResult",

    "PolicyEvaluator",

    "policy_evaluator",

        # Security Audit Framework

    "SecurityAuditEvent",

    "AuditRegistry",

    "audit_registry",


    # Security Compliance Framework

    "ComplianceControl",


    # Compliance Registry

    "ComplianceRegistry",

    "compliance_registry",


    # Module Permission Synchronization

    "ModulePermissionSynchronizer",

    "SYSTEM_ADMINISTRATOR_ROLE",


    # Governance Manager

    "SecurityGovernanceManager",

    "security_governance",

]

# ---------------------------------------------------------
# Module Permission Synchronization
# ---------------------------------------------------------

from app.core.security.module_permissions import (
    ModulePermissionSynchronizer,
    SYSTEM_ADMINISTRATOR_ROLE,
)
