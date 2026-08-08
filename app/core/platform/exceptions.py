"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Enterprise Exception & Error Handling.

Provides the common exception hierarchy
for platform infrastructure components.
"""


class CDCSPlatformException(Exception):
    """
    Base exception for all CDCS-EMP platform errors.
    """

    error_code = "PLATFORM_ERROR"

    def __init__(
        self,
        message: str = "",
        *,
        error_code: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(message)

        self.message = (
            message
            or self.__class__.__name__
        )

        self.error_code = (
            error_code
            or self.error_code
        )

        self.details = (
            dict(details)
            if details
            else {}
        )

    def to_dict(self) -> dict:
        """
        Return a serializable error representation.
        """

        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": dict(
                self.details
            ),
        }

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<{self.__class__.__name__} "
            f"error_code="
            f"{self.error_code!r} "
            f"message="
            f"{self.message!r}>"
        )


class PlatformConfigurationException(
    CDCSPlatformException
):
    """
    Raised when platform configuration fails.
    """

    error_code = "PLATFORM_CONFIGURATION_ERROR"


class PlatformRuntimeException(
    CDCSPlatformException
):
    """
    Raised when platform runtime initialization
    or execution fails.
    """

    error_code = "PLATFORM_RUNTIME_ERROR"


class PlatformContextException(
    CDCSPlatformException
):
    """
    Raised when platform context processing fails.
    """

    error_code = "PLATFORM_CONTEXT_ERROR"


class PlatformServiceException(
    CDCSPlatformException
):
    """
    Raised when platform service management fails.
    """

    error_code = "PLATFORM_SERVICE_ERROR"


class PlatformInfrastructureException(
    CDCSPlatformException
):
    """
    Raised for general platform infrastructure failures.
    """

    error_code = "PLATFORM_INFRASTRUCTURE_ERROR"


__all__ = [
    "CDCSPlatformException",
    "PlatformConfigurationException",
    "PlatformRuntimeException",
    "PlatformContextException",
    "PlatformServiceException",
    "PlatformInfrastructureException",
]
