"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration service composition and lifecycle management.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flask import Flask

from app.core.configuration.contracts import (
    ConfigurationProvider,
    ConfigurationRegistry,
)

from app.core.configuration.definition_registry import (
    DefaultConfigurationDefinitionRegistry,
)

from app.core.configuration.providers import (
    MemoryConfigurationProvider,
)

from app.core.configuration.resolution import (
    DefaultConfigurationResolver,
)

from app.core.configuration.service_impl import (
    DefaultConfigurationService,
)

from app.core.configuration.validator import (
    ConfigurationValidator,
)

from app.core.services import (
    ServiceNotRegisteredException,
    service_container,
)


CONFIGURATION_SERVICE_NAME = (
    "configuration"
)

CONFIGURATION_SERVICE_EXTENSION = (
    "configuration_service"
)


@dataclass(frozen=True, slots=True)
class ConfigurationServiceComponents:
    """
    Represents the composed configuration service
    dependencies.

    This object provides an explicit composition boundary
    for the configuration subsystem.
    """

    provider: ConfigurationProvider

    definition_registry: ConfigurationRegistry

    validator: ConfigurationValidator

    resolver: DefaultConfigurationResolver


def compose_configuration_service(
    provider: ConfigurationProvider,
    definition_registry: Optional[
        ConfigurationRegistry
    ] = None,
    validator: Optional[
        ConfigurationValidator
    ] = None,
    resolver: Optional[
        DefaultConfigurationResolver
    ] = None,
) -> DefaultConfigurationService:
    """
    Compose the default configuration service.

    Dependencies supplied by the caller are preserved.
    Missing dependencies are constructed using the
    default enterprise implementations.

    Args:
        provider:
            Configuration value provider.

        definition_registry:
            Optional configuration definition registry.

        validator:
            Optional configuration validator.

        resolver:
            Optional configuration resolver.

    Returns:
        A fully composed DefaultConfigurationService.
    """

    composed_validator = (
        validator
        or ConfigurationValidator()
    )

    composed_registry = (
        definition_registry
        or DefaultConfigurationDefinitionRegistry()
    )

    composed_resolver = (
        resolver
        or DefaultConfigurationResolver(
            validator=composed_validator
        )
    )

    return DefaultConfigurationService(
        provider=provider,
        definition_registry=composed_registry,
        resolver=composed_resolver,
        validator=composed_validator,
    )


def compose_default_configuration_service(
    provider: ConfigurationProvider,
) -> DefaultConfigurationService:
    """
    Compose a configuration service using all
    default enterprise configuration components.

    This is the preferred convenience composition
    entry point for application initialization.
    """

    return compose_configuration_service(
        provider=provider,
    )


def create_application_configuration_service(
    provider: Optional[
        ConfigurationProvider
    ] = None,
) -> DefaultConfigurationService:
    """
    Create the application configuration service.

    When no provider is supplied, the application uses
    the default in-memory configuration provider.

    A provider supplied by the caller is preserved and
    becomes the provider owned by the composed service.

    Args:
        provider:
            Optional configuration provider.

    Returns:
        A fully composed application configuration service.
    """

    if provider is None:
        application_provider = (
            MemoryConfigurationProvider()
        )
    else:
        application_provider = provider

    return compose_default_configuration_service(
        provider=application_provider,
    )


def register_configuration_service(
    app: Flask,
    provider: Optional[
        ConfigurationProvider
    ] = None,
) -> DefaultConfigurationService:
    """
    Compose and register the application configuration
    service.

    The same service instance is exposed through:

        1. Enterprise ServiceContainer
        2. Flask application extensions

    An optional provider may be supplied when the service
    is registered.

    Args:
        app:
            Flask application receiving the service
            extension.

        provider:
            Optional configuration provider.

    Returns:
        The registered configuration service.
    """

    service = (
        create_application_configuration_service(
            provider=provider,
        )
    )

    if service_container.has(
        CONFIGURATION_SERVICE_NAME
    ):
        service_container.remove(
            CONFIGURATION_SERVICE_NAME
        )

    service_container.register(
        CONFIGURATION_SERVICE_NAME,
        service,
    )

    app.extensions[
        CONFIGURATION_SERVICE_EXTENSION
    ] = service

    return service


def get_configuration_service(
) -> DefaultConfigurationService:
    """
    Retrieve the application configuration service
    from the enterprise ServiceContainer.

    Returns:
        The currently registered configuration service.

    Raises:
        RuntimeError:
            If the configuration service has not
            been registered.
    """

    try:
        service = service_container.resolve(
            CONFIGURATION_SERVICE_NAME
        )

    except ServiceNotRegisteredException as exc:
        raise RuntimeError(
            "Configuration service has not "
            "been registered."
        ) from exc

    if service is None:
        raise RuntimeError(
            "Configuration service has not "
            "been registered."
        )

    return service


def replace_configuration_provider(
    provider: ConfigurationProvider,
) -> DefaultConfigurationService:
    """
    Replace the provider used by the registered
    application configuration service.

    The existing service instance is preserved. Its
    definition registry, resolver, and validator are
    therefore retained while only the provider changes.

    Args:
        provider:
            New configuration provider.

    Returns:
        The existing configuration service with the
        replacement provider configured.

    Raises:
        ValueError:
            If provider is None.

        RuntimeError:
            If the configuration service has not
            been registered.
    """

    if provider is None:
        raise ValueError(
            "Configuration provider cannot be None."
        )

    service = get_configuration_service()

    service.provider = provider

    return service


def unregister_configuration_service(
    app: Optional[Flask] = None,
) -> None:
    """
    Unregister the application configuration service.

    The service is removed from the enterprise
    ServiceContainer. When an application is supplied,
    the corresponding Flask extension is removed as well.

    The operation is intentionally idempotent. Calling it
    when the service is not registered does not raise an
    exception.

    Args:
        app:
            Optional Flask application whose configuration
            service extension should also be removed.
    """

    if service_container.has(
        CONFIGURATION_SERVICE_NAME
    ):
        service_container.remove(
            CONFIGURATION_SERVICE_NAME
        )

    if app is not None:

        app.extensions.pop(
            CONFIGURATION_SERVICE_EXTENSION,
            None,
        )


__all__ = [
    "CONFIGURATION_SERVICE_NAME",
    "CONFIGURATION_SERVICE_EXTENSION",
    "ConfigurationServiceComponents",
    "compose_configuration_service",
    "compose_default_configuration_service",
    "create_application_configuration_service",
    "register_configuration_service",
    "get_configuration_service",
    "replace_configuration_provider",
    "unregister_configuration_service",
]
