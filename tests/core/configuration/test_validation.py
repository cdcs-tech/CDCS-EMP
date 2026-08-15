"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration validation semantics tests.
"""

import pytest

from app.core.configuration import (
    ConfigurationDefaultException,
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationRequiredException,
    ConfigurationTypeException,
    ConfigurationValidator,
)


def make_key(
    name: str = "test.setting",
) -> ConfigurationKey:
    """
    Create a standard platform configuration key.
    """

    return ConfigurationKey(
        name=name,
    )


def test_valid_value_passes_type_validation():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
    )

    result = ConfigurationValidator().validate(
        key,
        definition,
        "production",
    )

    assert result.valid is True
    assert result.value == "production"
    assert result.key == key
    assert result.definition == definition
    assert result.error is None


def test_invalid_value_type_is_rejected():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
    )

    with pytest.raises(
        ConfigurationTypeException,
        match="test\\.setting",
    ):
        ConfigurationValidator().validate(
            key,
            definition,
            123,
        )


def test_required_value_cannot_be_none():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        required=True,
    )

    with pytest.raises(
        ConfigurationRequiredException,
        match="Required configuration value is missing",
    ):
        ConfigurationValidator().validate(
            key,
            definition,
            None,
        )


def test_optional_none_value_is_allowed():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        required=False,
    )

    result = ConfigurationValidator().validate(
        key,
        definition,
        None,
    )

    assert result.valid is True
    assert result.value is None


def test_valid_default_passes_validation():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        default="development",
    )

    result = ConfigurationValidator().validate_default(
        key,
        definition,
    )

    assert result.valid is True
    assert result.value == "development"


def test_invalid_default_type_is_rejected():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        default=123,
    )

    with pytest.raises(
        ConfigurationDefaultException,
        match="Default value for configuration",
    ):
        ConfigurationValidator().validate_default(
            key,
            definition,
        )


def test_required_configuration_without_default_is_rejected():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        required=True,
        default=None,
    )

    with pytest.raises(
        ConfigurationDefaultException,
        match="has no default value",
    ):
        ConfigurationValidator().validate_default(
            key,
            definition,
        )


def test_optional_configuration_without_default_is_valid():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        required=False,
        default=None,
    )

    result = ConfigurationValidator().validate_default(
        key,
        definition,
    )

    assert result.valid is True
    assert result.value is None


def test_is_valid_returns_true_for_valid_value():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=int,
    )

    assert (
        ConfigurationValidator().is_valid(
            key,
            definition,
            42,
        )
        is True
    )


def test_is_valid_returns_false_for_invalid_type():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=int,
    )

    assert (
        ConfigurationValidator().is_valid(
            key,
            definition,
            "42",
        )
        is False
    )


def test_is_valid_returns_false_for_missing_required_value():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        required=True,
    )

    assert (
        ConfigurationValidator().is_valid(
            key,
            definition,
            None,
        )
        is False
    )


def test_is_default_valid_returns_true_for_valid_default():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=bool,
        default=True,
    )

    assert (
        ConfigurationValidator().is_default_valid(
            key,
            definition,
        )
        is True
    )


def test_is_default_valid_returns_false_for_invalid_default():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=bool,
        default="true",
    )

    assert (
        ConfigurationValidator().is_default_valid(
            key,
            definition,
        )
        is False
    )


def test_validation_does_not_mutate_definition():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=str,
        default="development",
    )

    ConfigurationValidator().validate(
        key,
        definition,
        "production",
    )

    assert definition.default == "development"
    assert definition.value_type is str


def test_default_validation_does_not_mutate_definition():

    key = make_key()

    definition = ConfigurationDefinition(
        name=key.name,
        value_type=int,
        default=10,
    )

    ConfigurationValidator().validate_default(
        key,
        definition,
    )

    assert definition.default == 10
    assert definition.value_type is int
