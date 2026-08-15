"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration domain tests.
"""

import inspect

import pytest

from app.core.configuration import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationProvider,
    ConfigurationRegistry,
    ConfigurationResolver,
    ConfigurationScope,
    ConfigurationValue,
)


def test_configuration_scopes_exist():

    assert (
        ConfigurationScope.PLATFORM.value
        == "platform"
    )

    assert (
        ConfigurationScope.MODULE.value
        == "module"
    )

    assert (
        ConfigurationScope.ORGANIZATION.value
        == "organization"
    )

    assert (
        ConfigurationScope.USER.value
        == "user"
    )


def test_platform_configuration_key():

    key = ConfigurationKey(
        name="app.name",
    )

    assert key.name == "app.name"

    assert (
        key.scope
        == ConfigurationScope.PLATFORM
    )


def test_module_configuration_key():

    key = ConfigurationKey(
        name="enabled",
        scope=ConfigurationScope.MODULE,
        module_code="finance",
    )

    assert key.name == "enabled"

    assert (
        key.scope
        == ConfigurationScope.MODULE
    )

    assert key.module_code == "finance"


def test_module_configuration_requires_module_code():

    with pytest.raises(
        ValueError,
        match="module code",
    ):
        ConfigurationKey(
            name="enabled",
            scope=ConfigurationScope.MODULE,
        )


def test_organization_configuration_requires_id():

    with pytest.raises(
        ValueError,
        match="organization ID",
    ):
        ConfigurationKey(
            name="currency",
            scope=ConfigurationScope.ORGANIZATION,
        )


def test_user_configuration_requires_id():

    with pytest.raises(
        ValueError,
        match="user ID",
    ):
        ConfigurationKey(
            name="theme",
            scope=ConfigurationScope.USER,
        )


def test_empty_configuration_key_name_rejected():

    with pytest.raises(
        ValueError,
        match="key name",
    ):
        ConfigurationKey(
            name="",
        )


def test_configuration_value():

    key = ConfigurationKey(
        name="currency",
    )

    value = ConfigurationValue(
        key=key,
        value="USD",
        source="platform",
        metadata={
            "description": "Default currency",
        },
    )

    assert value.key == key

    assert value.value == "USD"

    assert value.source == "platform"

    assert (
        value.metadata["description"]
        == "Default currency"
    )


def test_configuration_definition():

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
        default=100,
        required=True,
        description="Maximum number of items.",
    )

    assert definition.name == "max_items"

    assert definition.value_type is int

    assert definition.default == 100

    assert definition.required is True

    assert (
        definition.description
        == "Maximum number of items."
    )


def test_configuration_definition_type_validation():

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
    )

    assert (
        definition.validate_value(100)
        is True
    )

    assert (
        definition.validate_value("100")
        is False
    )


def test_optional_configuration_accepts_none():

    definition = ConfigurationDefinition(
        name="description",
        value_type=str,
        required=False,
    )

    assert (
        definition.validate_value(None)
        is True
    )


def test_required_configuration_rejects_none():

    definition = ConfigurationDefinition(
        name="description",
        value_type=str,
        required=True,
    )

    assert (
        definition.validate_value(None)
        is False
    )


def test_configuration_provider_is_abstract():

    assert inspect.isabstract(
        ConfigurationProvider
    )


def test_configuration_registry_is_abstract():

    assert inspect.isabstract(
        ConfigurationRegistry
    )


def test_configuration_resolver_is_abstract():

    assert inspect.isabstract(
        ConfigurationResolver
    )
