"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration domain models and contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ConfigurationScope(str, Enum):
    """
    Defines the scope at which a configuration
    value applies.
    """

    PLATFORM = "platform"
    MODULE = "module"
    ORGANIZATION = "organization"
    USER = "user"


@dataclass(frozen=True, slots=True)
class ConfigurationKey:
    """
    Identifies a configuration setting.
    """

    name: str

    scope: ConfigurationScope = (
        ConfigurationScope.PLATFORM
    )

    module_code: Optional[str] = None

    organization_id: Optional[str] = None

    user_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError(
                "Configuration key name is required."
            )

        if (
            self.scope == ConfigurationScope.MODULE
            and not self.module_code
        ):
            raise ValueError(
                "Module configuration requires "
                "a module code."
            )

        if (
            self.scope
            == ConfigurationScope.ORGANIZATION
            and not self.organization_id
        ):
            raise ValueError(
                "Organization configuration requires "
                "an organization ID."
            )

        if (
            self.scope == ConfigurationScope.USER
            and not self.user_id
        ):
            raise ValueError(
                "User configuration requires "
                "a user ID."
            )


@dataclass(frozen=True, slots=True)
class ConfigurationValue:
    """
    Represents a resolved configuration value.
    """

    key: ConfigurationKey

    value: Any

    source: str = "default"

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True, slots=True)
class ConfigurationDefinition:
    """
    Defines the contract for a configuration setting.
    """

    name: str

    value_type: type

    default: Any = None

    required: bool = False

    description: str = ""

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def validate_value(
        self,
        value: Any,
    ) -> bool:
        """
        Validate a value against the declared type.
        """

        if value is None:
            return not self.required

        return isinstance(
            value,
            self.value_type,
        )


__all__ = [
    "ConfigurationScope",
    "ConfigurationKey",
    "ConfigurationValue",
    "ConfigurationDefinition",
]
