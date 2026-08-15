"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration service behavioral tests.
"""

import pytest

from app.core.configuration import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationRequiredException,
    ConfigurationScope,
    ConfigurationTypeException,
    ConfigurationResolutionContext,
    DefaultConfigurationDefinitionRegistry,
    DefaultConfigurationResolver,
    DefaultConfigurationService,
    MemoryConfigurationProvider,
)


def create_service():
    """
    Create a default configuration service for testing.
    """

    provider = MemoryConfigurationProvider()

    definition_registry = (
        DefaultConfigurationDefinitionRegistry()
    )

    resolver = DefaultConfigurationResolver()

    return DefaultConfigurationService(
        provider=provider,
        definition_registry=definition_registry,
        resolver=resolver,
    )


def test_get_delegates_to_provider():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    service.set(
        key,
        "SSP",
    )

    result = service.get(
        key
    )

    assert result is not None

    assert result.key == key

    assert result.value == "SSP"


def test_get_returns_none_when_value_does_not_exist():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    assert (
        service.get(key)
        is None
    )


def test_set_delegates_to_provider():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    result = service.set(
        key,
        "SSP",
    )

    assert result.key == key

    assert result.value == "SSP"

    assert result.source == "memory"

    assert service.exists(
        key
    ) is True


def test_set_validates_registered_definition():

    service = create_service()

    service.register_definition(
        ConfigurationDefinition(
            name="currency",
            value_type=str,
        )
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


def test_set_rejects_invalid_value():

    service = create_service()

    service.register_definition(
        ConfigurationDefinition(
            name="currency",
            value_type=str,
        )
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    with pytest.raises(
        ConfigurationTypeException,
        match="currency",
    ):
        service.set(
            key,
            100,
        )

    assert (
        service.exists(key)
        is False
    )


def test_set_rejects_missing_required_value():

    service = create_service()

    service.register_definition(
        ConfigurationDefinition(
            name="currency",
            value_type=str,
            required=True,
        )
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    with pytest.raises(
        ConfigurationRequiredException,
        match="currency",
    ):
        service.set(
            key,
            None,
        )

    assert (
        service.exists(key)
        is False
    )


def test_delete_delegates_to_provider():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    service.set(
        key,
        "SSP",
    )

    assert service.delete(
        key
    ) is True

    assert service.exists(
        key
    ) is False


def test_delete_returns_false_for_missing_value():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    assert service.delete(
        key
    ) is False


def test_exists_delegates_to_provider():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    assert (
        service.exists(key)
        is False
    )

    service.set(
        key,
        "SSP",
    )

    assert (
        service.exists(key)
        is True
    )


def test_register_definition_delegates_to_registry():

    service = create_service()

    definition = ConfigurationDefinition(
        name="currency",
        value_type=str,
        default="SSP",
    )

    service.register_definition(
        definition
    )

    registered = service.get_definition(
        "currency"
    )

    assert registered is not None

    assert registered.name == "currency"

    assert registered.value_type is str

    assert registered.default == "SSP"


def test_register_definition_rejects_invalid_default():

    service = create_service()

    definition = ConfigurationDefinition(
        name="currency",
        value_type=str,
        default=100,
    )

    with pytest.raises(
        Exception,
        match="currency",
    ):
        service.register_definition(
            definition
        )


def test_get_definition_returns_none_for_unknown_definition():

    service = create_service()

    assert (
        service.get_definition(
            "unknown"
        )
        is None
    )


def test_resolve_platform_value():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    service.set(
        key,
        "SSP",
    )

    context = ConfigurationResolutionContext()

    assert (
        service.resolve(
            "currency",
            context,
        )
        == "SSP"
    )


def test_resolve_module_overrides_platform():

    service = create_service()

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.PLATFORM,
        ),
        "SSP",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.MODULE,
            module_code="finance",
        ),
        "USD",
    )

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    assert (
        service.resolve(
            "currency",
            context,
        )
        == "USD"
    )


def test_resolve_organization_overrides_module():

    service = create_service()

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.PLATFORM,
        ),
        "SSP",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.MODULE,
            module_code="finance",
        ),
        "USD",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.ORGANIZATION,
            organization_id="org-001",
        ),
        "EUR",
    )

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
    )

    assert (
        service.resolve(
            "currency",
            context,
        )
        == "EUR"
    )


def test_resolve_user_overrides_organization():

    service = create_service()

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.PLATFORM,
        ),
        "SSP",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.MODULE,
            module_code="finance",
        ),
        "USD",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.ORGANIZATION,
            organization_id="org-001",
        ),
        "EUR",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.USER,
            user_id="user-001",
        ),
        "GBP",
    )

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
        user_id="user-001",
    )

    assert (
        service.resolve(
            "currency",
            context,
        )
        == "GBP"
    )


def test_resolve_uses_registered_definition():

    service = create_service()

    service.register_definition(
        ConfigurationDefinition(
            name="tax_enabled",
            value_type=bool,
            default=False,
        )
    )

    service.set(
        ConfigurationKey(
            name="tax_enabled",
            scope=ConfigurationScope.PLATFORM,
        ),
        True,
    )

    context = ConfigurationResolutionContext()

    assert (
        service.resolve(
            "tax_enabled",
            context,
        )
        is True
    )


def test_resolve_rejects_value_that_violates_registered_definition():

    service = create_service()

    service.register_definition(
        ConfigurationDefinition(
            name="tax_enabled",
            value_type=bool,
            default=False,
        )
    )

    service.set(
        ConfigurationKey(
            name="tax_enabled",
            scope=ConfigurationScope.PLATFORM,
        ),
        True,
    )

    # The provider is intentionally populated directly
    # with an invalid value so that this test verifies
    # resolution-time validation independently from
    # set()-time validation.
    service.provider.set(
        ConfigurationKey(
            name="tax_enabled",
            scope=ConfigurationScope.PLATFORM,
        ),
        "yes",
    )

    context = ConfigurationResolutionContext()

    with pytest.raises(
        ConfigurationTypeException,
        match="tax_enabled",
    ):
        service.resolve(
            "tax_enabled",
            context,
        )


def test_resolve_returns_default_when_value_is_missing():

    service = create_service()

    context = ConfigurationResolutionContext()

    assert (
        service.resolve(
            "timezone",
            context,
            default="Africa/Juba",
        )
        == "Africa/Juba"
    )


def test_resolve_uses_explicit_definition():

    service = create_service()

    service.set(
        ConfigurationKey(
            name="max_users",
            scope=ConfigurationScope.PLATFORM,
        ),
        100,
    )

    definition = ConfigurationDefinition(
        name="max_users",
        value_type=int,
    )

    context = ConfigurationResolutionContext()

    assert (
        service.resolve(
            "max_users",
            context,
            definition=definition,
        )
        == 100
    )


def test_resolve_rejects_invalid_explicit_definition_value():

    service = create_service()

    service.provider.set(
        ConfigurationKey(
            name="max_users",
            scope=ConfigurationScope.PLATFORM,
        ),
        "100",
    )

    definition = ConfigurationDefinition(
        name="max_users",
        value_type=int,
    )

    context = ConfigurationResolutionContext()

    with pytest.raises(
        ConfigurationTypeException,
        match="max_users",
    ):
        service.resolve(
            "max_users",
            context,
            definition=definition,
        )


def test_resolution_does_not_mutate_provider_values():

    service = create_service()

    key = ConfigurationKey(
        name="settings",
        scope=ConfigurationScope.PLATFORM,
    )

    value = {
        "currency": "SSP",
    }

    service.set(
        key,
        value,
    )

    value["currency"] = "USD"

    stored = service.get(
        key
    )

    assert stored is not None

    assert (
        stored.value["currency"]
        == "SSP"
    )


def test_resolution_does_not_mutate_source_values():

    service = create_service()

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.PLATFORM,
        ),
        "SSP",
    )

    service.set(
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.MODULE,
            module_code="finance",
        ),
        "USD",
    )

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    assert (
        service.resolve(
            "currency",
            context,
        )
        == "USD"
    )

    assert (
        service.get(
            ConfigurationKey(
                name="currency",
                scope=ConfigurationScope.PLATFORM,
            )
        ).value
        == "SSP"
    )

    assert (
        service.get(
            ConfigurationKey(
                name="currency",
                scope=ConfigurationScope.MODULE,
                module_code="finance",
            )
        ).value
        == "USD"
    )


def test_service_does_not_store_values_independently():

    service = create_service()

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.PLATFORM,
    )

    service.set(
        key,
        "SSP",
    )

    assert len(
        service.provider
    ) == 1

    assert (
        service.get(key).value
        == "SSP"
    )
