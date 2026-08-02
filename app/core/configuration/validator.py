"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Validator

Validates module configuration requirements.
"""


from typing import Callable, Dict, List

from app.core.configuration.module import (
    ModuleConfiguration,
)


class ConfigurationValidationError(
    Exception
):
    """
    Raised when configuration validation fails.
    """

    pass


class ModuleConfigurationValidator:
    """
    Validates enterprise module configuration.
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


    def validate(self):
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


    def _validate_required_fields(self):
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


    def _validate_rules(self):
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
