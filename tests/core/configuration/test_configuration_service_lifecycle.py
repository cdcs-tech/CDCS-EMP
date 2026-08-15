"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration service lifecycle and provider management tests.
"""

import pytest
from flask import Flask

from app.core.configuration import (
    ConfigurationProvider,
    MemoryConfigurationProvider,
    replace_configuration_provider,
    register_configuration_service,
    unregister_configuration_service,
    get_configuration_service,
    create_application_configuration_service,
)

from app.core.services import (
    service_container,
)


@pytest.fixture
def app():
    """
    Create a minimal Flask application for lifecycle tests.
    """

    return Flask(
        __name__
    )


@pytest.fixture(autouse=True)
def clean_configuration_service():
    """
    Ensure the global configuration service registration
    is isolated between tests.
    """

    service_container.remove(
        "configuration"
    )

    yield

    service_container.remove(
        "configuration"
    )


def test_create_application_configuration_service_uses_default_provider():
    """
    The application configuration service uses the
    memory provider when no provider is supplied.
    """

    service = (
        create_application_configuration_service()
    )

    assert isinstance(
        service.provider,
        MemoryConfigurationProvider,
    )


def test_create_application_configuration_service_preserves_injected_provider():
    """
    An explicitly supplied provider is preserved by
    application service composition.
    """

    provider = MemoryConfigurationProvider()

    service = (
        create_application_configuration_service(
            provider=provider,
        )
    )

    assert service.provider is provider


def test_register_configuration_service_registers_in_service_container(
    app,
):
    """
    Registration exposes the configuration service through
    the enterprise service container.
    """

    service = register_configuration_service(
        app
    )

    assert (
        service_container.resolve(
            "configuration"
        )
        is service
    )


def test_register_configuration_service_registers_flask_extension(
    app,
):
    """
    Registration exposes the configuration service through
    Flask application extensions.
    """

    service = register_configuration_service(
        app
    )

    assert (
        app.extensions[
            "configuration_service"
        ]
        is service
    )


def test_register_configuration_service_uses_same_service_instance(
    app,
):
    """
    The service container and Flask extension must reference
    the same configuration service instance.
    """

    service = register_configuration_service(
        app
    )

    assert (
        service_container.resolve(
            "configuration"
        )
        is app.extensions[
            "configuration_service"
        ]
    )

    assert (
        service
        is app.extensions[
            "configuration_service"
        ]
    )


def test_register_configuration_service_preserves_injected_provider(
    app,
):
    """
    A provider supplied during application registration is
    preserved by the resulting service.
    """

    provider = MemoryConfigurationProvider()

    service = register_configuration_service(
        app,
        provider=provider,
    )

    assert service.provider is provider


def test_replace_configuration_provider_preserves_service_instance(
    app,
):
    """
    Replacing the provider does not recreate the
    configuration service.
    """

    service = register_configuration_service(
        app
    )

    original_service = service

    replacement = MemoryConfigurationProvider()

    result = replace_configuration_provider(
        replacement
    )

    assert result is original_service

    assert (
        service_container.resolve(
            "configuration"
        )
        is original_service
    )

    assert (
        app.extensions[
            "configuration_service"
        ]
        is original_service
    )


def test_replace_configuration_provider_updates_provider(
    app,
):
    """
    Provider replacement updates the provider used by
    the existing configuration service.
    """

    service = register_configuration_service(
        app
    )

    replacement = MemoryConfigurationProvider()

    result = replace_configuration_provider(
        replacement
    )

    assert result.provider is replacement


def test_replace_configuration_provider_preserves_registry(
    app,
):
    """
    Provider replacement preserves the existing definition
    registry.
    """

    service = register_configuration_service(
        app
    )

    registry = service.definition_registry

    replacement = MemoryConfigurationProvider()

    replace_configuration_provider(
        replacement
    )

    assert (
        service.definition_registry
        is registry
    )


def test_replace_configuration_provider_preserves_resolver(
    app,
):
    """
    Provider replacement preserves the existing resolver.
    """

    service = register_configuration_service(
        app
    )

    resolver = service.resolver

    replacement = MemoryConfigurationProvider()

    replace_configuration_provider(
        replacement
    )

    assert (
        service.resolver
        is resolver
    )


def test_replace_configuration_provider_preserves_validator(
    app,
):
    """
    Provider replacement preserves the existing validator.
    """

    service = register_configuration_service(
        app
    )

    validator = service.validator

    replacement = MemoryConfigurationProvider()

    replace_configuration_provider(
        replacement
    )

    assert (
        service.validator
        is validator
    )


def test_replace_configuration_provider_rejects_none(
    app,
):
    """
    Provider replacement rejects an invalid None provider.
    """

    register_configuration_service(
        app
    )

    with pytest.raises(
        ValueError,
        match="Configuration provider cannot be None",
    ):
        replace_configuration_provider(
            None
        )


def test_replace_configuration_provider_requires_registered_service():
    """
    Provider replacement requires an active configuration
    service registration.
    """

    provider = MemoryConfigurationProvider()

    with pytest.raises(
        RuntimeError,
        match="Configuration service has not been registered",
    ):
        replace_configuration_provider(
            provider
        )


def test_get_configuration_service_returns_registered_service(
    app,
):
    """
    The lifecycle getter returns the currently registered
    configuration service.
    """

    service = register_configuration_service(
        app
    )

    result = get_configuration_service()

    assert result is service


def test_unregister_configuration_service_removes_container_registration(
    app,
):
    """
    Unregistration removes the service from the enterprise
    service container.
    """

    register_configuration_service(
        app
    )

    unregister_configuration_service(
        app
    )

    assert not service_container.has(
        "configuration"
    )


def test_unregister_configuration_service_removes_flask_extension(
    app,
):
    """
    Unregistration removes the configuration service from
    Flask application extensions.
    """

    register_configuration_service(
        app
    )

    unregister_configuration_service(
        app
    )

    assert (
        "configuration_service"
        not in app.extensions
    )


def test_unregister_configuration_service_is_idempotent(
    app,
):
    """
    Repeated unregistration does not raise an exception.
    """

    register_configuration_service(
        app
    )

    unregister_configuration_service(
        app
    )

    unregister_configuration_service(
        app
    )

    assert not service_container.has(
        "configuration"
    )


def test_get_configuration_service_fails_after_unregister(
    app,
):
    """
    Retrieving the configuration service after
    unregistration raises the expected runtime error.
    """

    register_configuration_service(
        app
    )

    unregister_configuration_service(
        app
    )

    with pytest.raises(
        RuntimeError,
        match="Configuration service has not been registered",
    ):
        get_configuration_service()


def test_unregister_without_app_removes_container_registration(
    app,
):
    """
    Unregistration can remove the enterprise registration
    without requiring a Flask application.
    """

    register_configuration_service(
        app
    )

    unregister_configuration_service()

    assert not service_container.has(
        "configuration"
    )

    assert (
        app.extensions[
            "configuration_service"
        ]
        is not None
    )


def test_re_register_replaces_previous_service(
    app,
):
    """
    Registering a new configuration service replaces the
    previous service registration deterministically.
    """

    first_service = register_configuration_service(
        app
    )

    second_provider = MemoryConfigurationProvider()

    second_service = register_configuration_service(
        app,
        provider=second_provider,
    )

    assert second_service is not first_service

    assert (
        service_container.resolve(
            "configuration"
        )
        is second_service
    )

    assert (
        app.extensions[
            "configuration_service"
        ]
        is second_service
    )

    assert (
        second_service.provider
        is second_provider
    )


def test_replaced_provider_remains_operational(
    app,
):
    """
    The service remains operational after its provider
    has been replaced.
    """

    service = register_configuration_service(
        app
    )

    replacement = MemoryConfigurationProvider()

    replace_configuration_provider(
        replacement
    )

    from app.core.configuration import (
        ConfigurationKey,
        ConfigurationScope,
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    result = service.set(
        key,
        "SSP",
    )

    assert result.value == "SSP"

    assert service.get(
        key
    ).value == "SSP"
