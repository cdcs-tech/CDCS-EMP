"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Default configuration service implementation.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.configuration.contracts import (
    ConfigurationProvider,
    ConfigurationRegistry,
)

from app.core.configuration.domain import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationScope,
    ConfigurationValue,
)

from app.core.configuration.resolution import (
    ConfigurationResolutionContext,
    DefaultConfigurationResolver,
)

from app.core.configuration.service import (
    ConfigurationService,
)

from app.core.configuration.validator import (
    ConfigurationValidator,
)


class DefaultConfigurationService(
    ConfigurationService
):
    """
    Default concrete implementation of the
    application-facing configuration service.

    The service composes:

        - a configuration provider
        - a configuration definition registry
        - a configuration resolver
        - a configuration validator

    The service coordinates these components without
    taking ownership of their individual responsibilities.
    """

    def __init__(
        self,
        provider: ConfigurationProvider,
        definition_registry: ConfigurationRegistry,
        resolver: Optional[
            DefaultConfigurationResolver
        ] = None,
        validator: Optional[
            ConfigurationValidator
        ] = None,
    ) -> None:
        """
        Initialize the configuration service.

        Args:
            provider:
                Provider responsible for configuration
                value persistence.

            definition_registry:
                Registry responsible for configuration
                definitions.

            resolver:
                Optional configuration resolver.

            validator:
                Optional configuration validator.
        """

        self.provider = provider

        self.definition_registry = (
            definition_registry
        )

        self.validator = (
            validator
            or ConfigurationValidator()
        )

        self.resolver = (
            resolver
            or DefaultConfigurationResolver(
                validator=self.validator
            )
        )

    def get(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:
        """
        Retrieve a configuration value.

        Delegates persistence responsibility to the
        configured provider.
        """

        return self.provider.get(
            key
        )

    def set(
        self,
        key: ConfigurationKey,
        value: Any,
    ) -> ConfigurationValue:
        """
        Store or update a configuration value.

        When a definition exists for the configuration
        name, the value is validated before persistence.
        """

        definition = (
            self.get_definition(
                key.name
            )
        )

        if definition is not None:

            self.validator.validate(
                key,
                definition,
                value,
            )

        return self.provider.set(
            key,
            value,
        )

    def delete(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Delete a configuration value.

        Delegates deletion to the configured provider.
        """

        return self.provider.delete(
            key
        )

    def exists(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Determine whether a configuration value exists.

        Delegates existence checking to the configured
        provider.
        """

        return self.provider.exists(
            key
        )

    def get_definition(
        self,
        name: str,
    ) -> Optional[ConfigurationDefinition]:
        """
        Retrieve a configuration definition.

        Delegates definition lookup to the definition
        registry.
        """

        return (
            self.definition_registry.get_definition(
                name
            )
        )

    def register_definition(
        self,
        definition: ConfigurationDefinition,
    ) -> None:
        """
        Register a configuration definition.

        When a default value is explicitly supplied,
        the default is validated before registration.

        A required definition is permitted to have no
        default value. Required-value validation occurs
        when an actual configuration value is supplied
        or resolved.
        """

        validation_key = ConfigurationKey(
            name=definition.name,
            scope=ConfigurationScope.PLATFORM,
        )

        if definition.default is not None:

            self.validator.validate_default(
                validation_key,
                definition,
            )

        self.definition_registry.register(
            definition
        )

    def resolve(
        self,
        key: str,
        context: ConfigurationResolutionContext,
        default: Any = None,
        definition: Optional[
            ConfigurationDefinition
        ] = None,
    ) -> Any:
        """
        Resolve the effective configuration value.

        Values are collected from the provider for each
        applicable scope. Scope precedence remains the
        responsibility of the resolver.
        """

        values: dict[
            ConfigurationScope,
            dict[str, Any],
        ] = {}

        scope_contexts = {
            ConfigurationScope.PLATFORM: ConfigurationKey(
                name=key,
                scope=ConfigurationScope.PLATFORM,
            ),
            ConfigurationScope.MODULE: (
                ConfigurationKey(
                    name=key,
                    scope=ConfigurationScope.MODULE,
                    module_code=context.module_code,
                )
                if context.module_code
                else None
            ),
            ConfigurationScope.ORGANIZATION: (
                ConfigurationKey(
                    name=key,
                    scope=ConfigurationScope.ORGANIZATION,
                    organization_id=(
                        context.organization_id
                    ),
                )
                if context.organization_id
                else None
            ),
            ConfigurationScope.USER: (
                ConfigurationKey(
                    name=key,
                    scope=ConfigurationScope.USER,
                    user_id=context.user_id,
                )
                if context.user_id
                else None
            ),
        }

        for scope, configuration_key in (
            scope_contexts.items()
        ):

            if configuration_key is None:
                continue

            stored = self.provider.get(
                configuration_key
            )

            if stored is None:
                continue

            values.setdefault(
                scope,
                {},
            )[key] = stored.value

        effective_definition = definition

        if effective_definition is None:

            effective_definition = (
                self.get_definition(
                    key
                )
            )

        if isinstance(
            self.resolver,
            DefaultConfigurationResolver,
        ):
            return self.resolver.resolve(
                values,
                key,
                context,
                default=default,
                definition=effective_definition,
            )

        configuration_key = ConfigurationKey(
            name=key,
            scope=ConfigurationScope.PLATFORM,
        )

        result = self.resolver.resolve(
            configuration_key,
        )

        if isinstance(
            result,
            ConfigurationValue,
        ):
            return result.value

        return result


__all__ = [
    "DefaultConfigurationService",
]
