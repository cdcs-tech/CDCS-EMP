"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration validation contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.core.configuration.domain import (
    ConfigurationDefinition,
    ConfigurationKey,
)


class ConfigurationValidationException(
    Exception
):
    """
    Base exception for configuration validation
    failures.
    """


class ConfigurationTypeException(
    ConfigurationValidationException
):
    """
    Raised when a configuration value does not
    match its declared type.
    """


class ConfigurationRequiredException(
    ConfigurationValidationException
):
    """
    Raised when a required configuration value
    is missing.
    """


class ConfigurationDefaultException(
    ConfigurationValidationException
):
    """
    Raised when a configuration default value
    violates its declared definition.
    """


@dataclass(frozen=True, slots=True)
class ConfigurationValidationResult:
    """
    Represents the result of validating a
    configuration value.
    """

    valid: bool

    key: ConfigurationKey

    value: Any = None

    definition: Optional[
        ConfigurationDefinition
    ] = None

    error: Optional[str] = None

    @classmethod
    def success(
        cls,
        key: ConfigurationKey,
        value: Any,
        definition: Optional[
            ConfigurationDefinition
        ] = None,
    ) -> "ConfigurationValidationResult":
        """
        Create a successful validation result.
        """

        return cls(
            valid=True,
            key=key,
            value=value,
            definition=definition,
        )

    @classmethod
    def failure(
        cls,
        key: ConfigurationKey,
        error: str,
        value: Any = None,
        definition: Optional[
            ConfigurationDefinition
        ] = None,
    ) -> "ConfigurationValidationResult":
        """
        Create a failed validation result.
        """

        return cls(
            valid=False,
            key=key,
            value=value,
            definition=definition,
            error=error,
        )


__all__ = [
    "ConfigurationValidationException",
    "ConfigurationTypeException",
    "ConfigurationRequiredException",
    "ConfigurationDefaultException",
    "ConfigurationValidationResult",
]
