"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration registry tests.
"""

import pytest

from app.core.configuration import (
    ConfigurationContractException,
    DefaultConfigurationRegistry,
    ModuleConfiguration,
)


def test_registry_starts_empty():

    registry = DefaultConfigurationRegistry()

    assert len(registry) == 0


def test_register_configuration():

    registry = DefaultConfigurationRegistry()

    configuration = ModuleConfiguration(
        module_code="finance",
        settings={
            "currency": "SSP",
        },
    )

    registered = registry.register(
        configuration
    )

    assert registered.module_code == "finance"

    assert (
        registered.get("currency")
        == "SSP"
    )

    assert len(registry) == 1


def test_registry_contains_registered_module():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance"
        )
    )

    assert (
        registry.contains("finance")
        is True
    )

    assert (
        registry.contains("unknown")
        is False
    )


def test_get_returns_configuration():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance",
            settings={
                "currency": "SSP",
            },
        )
    )

    configuration = registry.get(
        "finance"
    )

    assert (
        configuration.module_code
        == "finance"
    )

    assert (
        configuration.get("currency")
        == "SSP"
    )


def test_get_returns_independent_copy():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance",
            settings={
                "currency": "SSP",
            },
        )
    )

    configuration = registry.get(
        "finance"
    )

    configuration.set(
        "currency",
        "USD",
    )

    stored = registry.get(
        "finance"
    )

    assert (
        stored.get("currency")
        == "SSP"
    )


def test_duplicate_registration_is_rejected():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance"
        )
    )

    with pytest.raises(
        ConfigurationContractException,
        match="already registered",
    ):
        registry.register(
            ModuleConfiguration(
                module_code="finance"
            )
        )


def test_invalid_registration_is_rejected():

    registry = DefaultConfigurationRegistry()

    with pytest.raises(
        ConfigurationContractException,
        match="requires a ModuleConfiguration",
    ):
        registry.register(
            object()
        )


def test_empty_module_code_is_rejected():

    registry = DefaultConfigurationRegistry()

    configuration = ModuleConfiguration(
        module_code=""
    )

    with pytest.raises(
        ConfigurationContractException,
        match="module code",
    ):
        registry.register(
            configuration
        )


def test_unknown_configuration_is_rejected():

    registry = DefaultConfigurationRegistry()

    with pytest.raises(
        ConfigurationContractException,
        match="No configuration is registered",
    ):
        registry.get(
            "finance"
        )


def test_resolve_without_overrides():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance",
            settings={
                "currency": "SSP",
                "tax_enabled": True,
            },
        )
    )

    resolved = registry.resolve(
        "finance"
    )

    assert (
        resolved.get("currency")
        == "SSP"
    )

    assert (
        resolved.get("tax_enabled")
        is True
    )


def test_resolve_applies_overrides():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance",
            settings={
                "currency": "SSP",
                "tax_enabled": True,
            },
        )
    )

    resolved = registry.resolve(
        "finance",
        {
            "currency": "USD",
            "tax_enabled": False,
        },
    )

    assert (
        resolved.get("currency")
        == "USD"
    )

    assert (
        resolved.get("tax_enabled")
        is False
    )


def test_resolve_does_not_mutate_registered_configuration():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance",
            settings={
                "currency": "SSP",
            },
        )
    )

    resolved = registry.resolve(
        "finance",
        {
            "currency": "USD",
        },
    )

    assert (
        resolved.get("currency")
        == "USD"
    )

    registered = registry.get(
        "finance"
    )

    assert (
        registered.get("currency")
        == "SSP"
    )


def test_invalid_overrides_are_rejected():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance"
        )
    )

    with pytest.raises(
        ConfigurationContractException,
        match="overrides must",
    ):
        registry.resolve(
            "finance",
            ["invalid"],
        )


def test_unregister_returns_configuration():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance",
            settings={
                "currency": "SSP",
            },
        )
    )

    removed = registry.unregister(
        "finance"
    )

    assert (
        removed.module_code
        == "finance"
    )

    assert (
        removed.get("currency")
        == "SSP"
    )

    assert (
        registry.contains("finance")
        is False
    )

    assert len(registry) == 0


def test_unregister_unknown_configuration_is_rejected():

    registry = DefaultConfigurationRegistry()

    with pytest.raises(
        ConfigurationContractException,
        match="No configuration is registered",
    ):
        registry.unregister(
            "finance"
        )


def test_clear_removes_all_configurations():

    registry = DefaultConfigurationRegistry()

    registry.register(
        ModuleConfiguration(
            module_code="finance"
        )
    )

    registry.register(
        ModuleConfiguration(
            module_code="hr"
        )
    )

    assert len(registry) == 2

    registry.clear()

    assert len(registry) == 0

    assert (
        registry.contains("finance")
        is False
    )

    assert (
        registry.contains("hr")
        is False
    )
