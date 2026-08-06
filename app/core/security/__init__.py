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

]
