"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration exceptions.
"""


class ConfigurationException(Exception):
    """
    Base exception for configuration errors.
    """


class ConfigurationContractException(
    ConfigurationException
):
    """
    Raised when a configuration contract is violated.
    """


class ConfigurationNotFoundException(
    ConfigurationException
):
    """
    Raised when required configuration cannot be found.
    """


class ConfigurationValidationException(
    ConfigurationException
):
    """
    Raised when a configuration value is invalid.
    """


class ConfigurationScopeException(
    ConfigurationException
):
    """
    Raised when configuration scope is invalid.
    """


__all__ = [
    "ConfigurationException",
    "ConfigurationContractException",
    "ConfigurationNotFoundException",
    "ConfigurationValidationException",
    "ConfigurationScopeException",
]
