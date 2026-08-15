"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration resolution semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from app.core.configuration.domain import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationScope,
)

from app.core.configuration.validator import (
    ConfigurationValidator,
)


@dataclass(frozen=True, slots=True)
class ConfigurationResolutionContext:
    """
    Identifies the scopes available during
    configuration resolution.
    """

    module_code: Optional[str] = None

    organization_id: Optional[str] = None

    user_id: Optional[str] = None


class DefaultConfigurationResolver:
    """
    Resolves configuration values according
    to enterprise scope precedence.

    Resolution determines the effective value.
    Validation determines whether the effective
    value satisfies its configuration definition.

    Precedence, from lowest to highest:

        PLATFORM
        MODULE
        ORGANIZATION
        USER
    """

    SCOPE_PRECEDENCE = (
        ConfigurationScope.PLATFORM,
        ConfigurationScope.MODULE,
        ConfigurationScope.ORGANIZATION,
        ConfigurationScope.USER,
    )

    def __init__(
        self,
        validator: Optional[
            ConfigurationValidator
        ] = None,
    ) -> None:
        """
        Initialize the configuration resolver.

        Args:
            validator:
                Optional configuration validator.
                When supplied, resolved values can be
                validated against configuration definitions.
        """

        self.validator = validator

    def resolve(
        self,
        values: Mapping[
            ConfigurationScope,
            Mapping[str, Any],
        ],
        key: str,
        context: ConfigurationResolutionContext,
        default: Any = None,
        definition: Optional[
            ConfigurationDefinition
        ] = None,
    ) -> Any:
        """
        Resolve a configuration value.

        More-specific scopes override broader scopes.

        When a configuration definition is supplied,
        the effective value is validated after
        resolution.
        """

        resolved = default

        for scope in self.SCOPE_PRECEDENCE:

            scope_values = values.get(
                scope,
                {},
            )

            if key not in scope_values:
                continue

            if not self._scope_applies(
                scope,
                context,
            ):
                continue

            resolved = scope_values[key]

        if definition is not None:

            validator = (
                self.validator
                or ConfigurationValidator()
            )

            configuration_key = ConfigurationKey(
                name=key,
                scope=ConfigurationScope.PLATFORM,
            )

            validator.validate(
                configuration_key,
                definition,
                resolved,
            )

        return resolved

    def resolve_all(
        self,
        values: Mapping[
            ConfigurationScope,
            Mapping[str, Any],
        ],
        context: ConfigurationResolutionContext,
    ) -> dict[str, Any]:
        """
        Resolve all configuration values available
        for the supplied context.
        """

        keys: set[str] = set()

        for scope_values in values.values():
            keys.update(
                scope_values.keys()
            )

        return {
            key: self.resolve(
                values,
                key,
                context,
            )
            for key in keys
        }

    def _scope_applies(
        self,
        scope: ConfigurationScope,
        context: ConfigurationResolutionContext,
    ) -> bool:
        """
        Determine whether a configuration scope
        applies to the supplied context.
        """

        if scope == ConfigurationScope.PLATFORM:
            return True

        if scope == ConfigurationScope.MODULE:
            return bool(
                context.module_code
            )

        if scope == ConfigurationScope.ORGANIZATION:
            return bool(
                context.organization_id
            )

        if scope == ConfigurationScope.USER:
            return bool(
                context.user_id
            )

        return False


__all__ = [
    "ConfigurationResolutionContext",
    "DefaultConfigurationResolver",
]
