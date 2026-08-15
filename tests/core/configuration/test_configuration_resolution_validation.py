"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration resolution validation integration tests.
"""

import pytest

from app.core.configuration import (
    ConfigurationDefinition,
    ConfigurationResolutionContext,
    ConfigurationRequiredException,
    ConfigurationScope,
    ConfigurationTypeException,
    DefaultConfigurationResolver,
)


def test_resolved_value_is_validated_against_definition():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "max_items": 100,
        },
    }

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
        required=True,
    )

    context = ConfigurationResolutionContext()

    resolved = resolver.resolve(
        values,
        "max_items",
        context,
        definition=definition,
    )

    assert resolved == 100


def test_invalid_resolved_value_is_rejected():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "max_items": "100",
        },
    }

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
        required=True,
    )

    context = ConfigurationResolutionContext()

    with pytest.raises(
        ConfigurationTypeException,
        match="max_items",
    ):
        resolver.resolve(
            values,
            "max_items",
            context,
            definition=definition,
        )


def test_required_resolved_value_is_rejected():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "max_items": None,
        },
    }

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
        required=True,
    )

    context = ConfigurationResolutionContext()

    with pytest.raises(
        ConfigurationRequiredException,
        match="max_items",
    ):
        resolver.resolve(
            values,
            "max_items",
            context,
            definition=definition,
        )


def test_more_specific_scope_is_resolved_before_validation():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "max_items": 100,
        },
        ConfigurationScope.MODULE: {
            "max_items": "invalid",
        },
    }

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
        required=True,
    )

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    with pytest.raises(
        ConfigurationTypeException,
        match="max_items",
    ):
        resolver.resolve(
            values,
            "max_items",
            context,
            definition=definition,
        )


def test_valid_more_specific_scope_is_accepted():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "max_items": 100,
        },
        ConfigurationScope.MODULE: {
            "max_items": 250,
        },
    }

    definition = ConfigurationDefinition(
        name="max_items",
        value_type=int,
        required=True,
    )

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    resolved = resolver.resolve(
        values,
        "max_items",
        context,
        definition=definition,
    )

    assert resolved == 250


def test_resolution_without_definition_preserves_existing_behavior():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "max_items": "100",
        },
    }

    context = ConfigurationResolutionContext()

    resolved = resolver.resolve(
        values,
        "max_items",
        context,
    )

    assert resolved == "100"
