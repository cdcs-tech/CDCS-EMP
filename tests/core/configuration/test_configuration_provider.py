"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

In-memory configuration provider tests.
"""

import inspect

from app.core.configuration import (
    ConfigurationKey,
    ConfigurationProvider,
    ConfigurationScope,
    ConfigurationValue,
    MemoryConfigurationProvider,
)


def test_configuration_provider_is_abstract():

    assert inspect.isabstract(
        ConfigurationProvider
    )


def test_memory_provider_is_concrete():

    assert not inspect.isabstract(
        MemoryConfigurationProvider
    )


def test_memory_provider_starts_empty():

    provider = (
        MemoryConfigurationProvider()
    )

    assert len(provider) == 0


def test_get_returns_none_for_missing_key():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    assert provider.get(
        key
    ) is None


def test_set_stores_configuration_value():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    stored = provider.set(
        key,
        "SSP",
    )

    assert isinstance(
        stored,
        ConfigurationValue,
    )

    assert stored.key == key

    assert stored.value == "SSP"

    assert stored.source == "memory"


def test_get_returns_stored_value():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    provider.set(
        key,
        "SSP",
    )

    value = provider.get(
        key
    )

    assert value is not None

    assert value.key == key

    assert value.value == "SSP"

    assert value.source == "memory"


def test_exists_returns_true_for_registered_key():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    provider.set(
        key,
        "SSP",
    )

    assert provider.exists(
        key
    ) is True


def test_exists_returns_false_for_missing_key():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    assert provider.exists(
        key
    ) is False


def test_delete_removes_existing_value():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    provider.set(
        key,
        "SSP",
    )

    assert provider.delete(
        key
    ) is True

    assert provider.exists(
        key
    ) is False

    assert provider.get(
        key
    ) is None


def test_delete_returns_false_for_missing_value():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    assert provider.delete(
        key
    ) is False


def test_set_replaces_existing_value():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
    )

    provider.set(
        key,
        "SSP",
    )

    provider.set(
        key,
        "USD",
    )

    value = provider.get(
        key
    )

    assert value is not None

    assert value.value == "USD"

    assert len(provider) == 1


def test_get_returns_independent_copy():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="settings",
    )

    provider.set(
        key,
        {
            "currency": "SSP",
        },
    )

    value = provider.get(
        key
    )

    assert value is not None

    value.value[
        "currency"
    ] = "USD"

    stored = provider.get(
        key
    )

    assert stored is not None

    assert (
        stored.value[
            "currency"
        ]
        == "SSP"
    )


def test_set_does_not_retain_mutable_input_reference():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="settings",
    )

    settings = {
        "currency": "SSP",
    }

    provider.set(
        key,
        settings,
    )

    settings[
        "currency"
    ] = "USD"

    stored = provider.get(
        key
    )

    assert stored is not None

    assert (
        stored.value[
            "currency"
        ]
        == "SSP"
    )


def test_set_returns_independent_copy():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="settings",
    )

    stored = provider.set(
        key,
        {
            "currency": "SSP",
        },
    )

    stored.value[
        "currency"
    ] = "USD"

    current = provider.get(
        key
    )

    assert current is not None

    assert (
        current.value[
            "currency"
        ]
        == "SSP"
    )


def test_clear_removes_all_values():

    provider = (
        MemoryConfigurationProvider()
    )

    provider.set(
        ConfigurationKey(
            name="currency",
        ),
        "SSP",
    )

    provider.set(
        ConfigurationKey(
            name="timezone",
        ),
        "Africa/Juba",
    )

    assert len(provider) == 2

    provider.clear()

    assert len(provider) == 0


def test_configuration_scope_is_preserved_in_key():

    provider = (
        MemoryConfigurationProvider()
    )

    key = ConfigurationKey(
        name="currency",
        scope=ConfigurationScope.MODULE,
        module_code="finance",
    )

    provider.set(
        key,
        "SSP",
    )

    value = provider.get(
        key
    )

    assert value is not None

    assert (
        value.key.scope
        == ConfigurationScope.MODULE
    )

    assert (
        value.key.module_code
        == "finance"
    )
