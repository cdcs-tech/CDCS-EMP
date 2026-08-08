"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Platform configuration tests.
"""

from app.core.platform import (
    PlatformConfig,
)


def test_default_configuration():

    config = PlatformConfig()

    assert (
        config.environment
        == "development"
    )

    assert (
        config.debug
        is False
    )

    assert (
        config.testing
        is False
    )

    assert (
        config.log_level
        == "INFO"
    )

    assert (
        config.app_version
        == "1.0.0"
    )


def test_configuration_validation():

    config = PlatformConfig()

    assert (
        config.validate()
        is True
    )


def test_development_environment():

    config = PlatformConfig(
        environment="development"
    )

    assert (
        config.is_development
        is True
    )

    assert (
        config.is_testing
        is False
    )

    assert (
        config.is_production
        is False
    )


def test_testing_environment():

    config = PlatformConfig(
        environment="testing"
    )

    assert (
        config.is_testing
        is True
    )


def test_production_environment():

    config = PlatformConfig(
        environment="production"
    )

    assert (
        config.is_production
        is True
    )


def test_environment_configuration(
    monkeypatch,
):

    monkeypatch.setenv(
        "CDCS_ENVIRONMENT",
        "testing",
    )

    monkeypatch.setenv(
        "CDCS_DEBUG",
        "true",
    )

    monkeypatch.setenv(
        "CDCS_TESTING",
        "true",
    )

    monkeypatch.setenv(
        "CDCS_LOG_LEVEL",
        "DEBUG",
    )

    monkeypatch.setenv(
        "CDCS_APP_VERSION",
        "2.0.0",
    )

    config = (
        PlatformConfig.from_environment()
    )

    assert (
        config.environment
        == "testing"
    )

    assert (
        config.debug
        is True
    )

    assert (
        config.testing
        is True
    )

    assert (
        config.log_level
        == "DEBUG"
    )

    assert (
        config.app_version
        == "2.0.0"
    )


def test_invalid_configuration():

    config = PlatformConfig(
        environment=""
    )

    try:

        config.validate()

    except ValueError as exc:

        assert (
            "environment"
            in str(exc).lower()
        )

    else:

        raise AssertionError(
            "Expected ValueError"
        )


def test_configuration_repr():

    config = PlatformConfig()

    representation = repr(
        config
    )

    assert (
        "PlatformConfig"
        in representation
    )

    assert (
        "environment="
        in representation
    )

