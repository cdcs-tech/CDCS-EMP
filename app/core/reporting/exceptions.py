"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Reporting-specific exception hierarchy.
"""


class ReportingException(Exception):
    """
    Base exception for reporting framework failures.

    All reporting-related framework exceptions should
    inherit from this exception so callers can catch
    reporting failures at a common abstraction boundary.
    """


class ReportingConfigurationException(
    ReportingException
):
    """
    Raised when reporting configuration is invalid.
    """


class ReportingContractException(
    ReportingException
):
    """
    Raised when a reporting contract is invalid
    or cannot be satisfied.
    """


class ReportDefinitionException(
    ReportingException
):
    """
    Raised when a report definition is invalid.
    """


class ReportExecutionException(
    ReportingException
):
    """
    Raised when report execution fails.
    """


class ReportValidationException(
    ReportingException
):
    """
    Raised when report input or output validation fails.
    """


class ReportNotFoundException(
    ReportingException
):
    """
    Raised when a requested report cannot be found.
    """


class ReportRegistrationException(
    ReportingException
):
    """
    Raised when report registration fails.
    """


class AnalyticsException(
    ReportingException
):
    """
    Base exception for analytics-related failures.
    """


class AnalyticsConfigurationException(
    AnalyticsException
):
    """
    Raised when analytics configuration is invalid.
    """


class AnalyticsExecutionException(
    AnalyticsException
):
    """
    Raised when an analytics operation fails.
    """


__all__ = [
    "ReportingException",
    "ReportingConfigurationException",
    "ReportingContractException",
    "ReportDefinitionException",
    "ReportExecutionException",
    "ReportValidationException",
    "ReportNotFoundException",
    "ReportRegistrationException",
    "AnalyticsException",
    "AnalyticsConfigurationException",
    "AnalyticsExecutionException",
]
