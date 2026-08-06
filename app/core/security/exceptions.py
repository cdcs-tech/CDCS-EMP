"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security exception hierarchy.
"""


class SecurityException(Exception):
    """
    Base exception for security-related failures.
    """

    pass



class AuthenticationError(SecurityException):
    """
    Raised when authentication fails.
    """

    pass



class AuthorizationError(SecurityException):
    """
    Raised when a user is not authorized.
    """

    pass



class PermissionDeniedError(AuthorizationError):
    """
    Raised when required permission is missing.
    """

    pass



class SecurityPolicyViolationError(SecurityException):
    """
    Raised when a security policy is violated.
    """

    pass
