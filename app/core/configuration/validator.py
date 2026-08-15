"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration validation services.

Provides both:

- legacy/module configuration validation
- enterprise configuration definition/value validation
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from app.core.configuration.domain import (
    ConfigurationDefinition,
    ConfigurationKey,
)

from app.core.configuration.module import (
    ModuleConfiguration,
)

from app.core.configuration.validation import (
    ConfigurationDefaultException,
    ConfigurationRequiredException,
    ConfigurationTypeException,
    ConfigurationValidationResult,
)


class ConfigurationValidationError(
    Exception
):
    """
    Raised when module configuration validation
    fails.

    Preserved for compatibility with the existing
    ModuleConfigurationValidator contract.
    """

    pass


class ModuleConfigurationValidator:
    """
    Validates enterprise module configuration.

    This validator is retained as the module-level
    configuration validator established before the
    enterprise configuration validation framework.
    """

    def __init__(
        self,
        configuration: ModuleConfiguration,
    ):
        """
        Initialize validator.

        Args:
            configuration:
                Module configuration instance.
        """

        self.configuration = configuration

        self.required_fields: List[str] = []

        self.rules: List[
            Callable
        ] = []

    def require(
        self,
        key: str,
    ):
        """
        Register a required configuration key.
        """

        self.required_fields.append(
            key
        )

        return self

    def add_rule(
        self,
        rule: Callable,
    ):
        """
        Register custom validation rule.
        """

        self.rules.append(
            rule
        )

        return self

    def validate(
        self,
    ):
        """
        Validate configuration.

        Returns:
            True

        Raises:
            ConfigurationValidationError
        """

        self._validate_required_fields()

        self._validate_rules()

        return True

    def _validate_required_fields(
        self,
    ):
        """
        Validate required fields exist.
        """

        missing = [
            field
            for field
            in self.required_fields
            if not self.configuration.has(
                field
            )
        ]

        if missing:
            raise ConfigurationValidationError(
                "Missing required configuration "
                f"fields: {missing}"
            )

    def _validate_rules(
        self,
    ):
        """
        Execute custom validation rules.
        """

        for rule in self.rules:

            result = rule(
                self.configuration
            )

            if result is False:
                raise ConfigurationValidationError(
                    "Configuration validation rule failed."
                )


class ConfigurationValidator:
    """
    Validates enterprise configuration values
    against ConfigurationDefinition contracts.
    """

    def validate(
        self,
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
        value: Any,
    ) -> ConfigurationValidationResult:
        """
        Validate a configuration value.

        Validation order:

            1. Required-value validation
            2. Type validation
        """

        if value is None:

            if definition.required:
                raise ConfigurationRequiredException(
                    self._required_message(
                        key
                    )
                )

            return ConfigurationValidationResult.success(
                key=key,
                value=value,
                definition=definition,
            )

        if not isinstance(
            value,
            definition.value_type,
        ):
            raise ConfigurationTypeException(
                self._type_message(
                    key,
                    definition,
                    value,
                )
            )

        return ConfigurationValidationResult.success(
            key=key,
            value=value,
            definition=definition,
        )

    def validate_default(
        self,
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
    ) -> ConfigurationValidationResult:
        """
        Validate the default value declared by
        a configuration definition.
        """

        default = definition.default

        if default is None:

            if definition.required:
                raise ConfigurationDefaultException(
                    self._default_required_message(
                        key
                    )
                )

            return ConfigurationValidationResult.success(
                key=key,
                value=default,
                definition=definition,
            )

        if not isinstance(
            default,
            definition.value_type,
        ):
            raise ConfigurationDefaultException(
                self._default_type_message(
                    key,
                    definition,
                    default,
                )
            )

        return ConfigurationValidationResult.success(
            key=key,
            value=default,
            definition=definition,
        )

    def is_valid(
        self,
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
        value: Any,
    ) -> bool:
        """
        Return whether a configuration value is valid.
        """

        try:

            self.validate(
                key,
                definition,
                value,
            )

        except (
            ConfigurationRequiredException,
            ConfigurationTypeException,
        ):
            return False

        return True

    def is_default_valid(
        self,
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
    ) -> bool:
        """
        Return whether a configuration default is valid.
        """

        try:

            self.validate_default(
                key,
                definition,
            )

        except ConfigurationDefaultException:
            return False

        return True

    @staticmethod
    def _required_message(
        key: ConfigurationKey,
    ) -> str:
        """
        Build a required-value validation message.
        """

        return (
            "Required configuration value is missing: "
            f"'{key.name}'."
        )

    @staticmethod
    def _type_message(
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
        value: Any,
    ) -> str:
        """
        Build a type validation message.
        """

        return (
            f"Configuration '{key.name}' must be "
            f"of type "
            f"{definition.value_type.__name__}; "
            f"received "
            f"{type(value).__name__}."
        )

    @staticmethod
    def _default_required_message(
        key: ConfigurationKey,
    ) -> str:
        """
        Build a missing required-default message.
        """

        return (
            "Required configuration "
            f"'{key.name}' has no default value."
        )

    @staticmethod
    def _default_type_message(
        key: ConfigurationKey,
        definition: ConfigurationDefinition,
        default: Any,
    ) -> str:
        """
        Build an invalid-default message.
        """

        return (
            f"Default value for configuration "
            f"'{key.name}' must be of type "
            f"{definition.value_type.__name__}; "
            f"received "
            f"{type(default).__name__}."
        )


__all__ = [
    "ConfigurationValidationError",
    "ModuleConfigurationValidator",
    "ConfigurationValidator",
]
