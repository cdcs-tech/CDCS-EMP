"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Runtime context tests.
"""

from app.core.platform import (
    PlatformConfig,
    RuntimeContext,
)


def test_runtime_context_creation():

    config = PlatformConfig(
        environment="development",
        debug=True,
        testing=False,
        app_name="CDCS-EMP",
        app_version="1.0.0",
    )

    runtime = RuntimeContext(
        config=config
    )

    assert (
        runtime.application_name
        == "CDCS-EMP"
    )

    assert (
        runtime.application_version
        == "1.0.0"
    )

    assert (
        runtime.environment
        == "development"
    )

    assert (
        runtime.debug
        is True
    )


def test_runtime_environment_flags():

    development = RuntimeContext(
        config=PlatformConfig(
            environment="development"
        )
    )

    testing = RuntimeContext(
        config=PlatformConfig(
            environment="testing"
        )
    )

    production = RuntimeContext(
        config=PlatformConfig(
            environment="production"
        )
    )

    assert (
        development.is_development
        is True
    )

    assert (
        development.is_testing
        is False
    )

    assert (
        production.is_production
        is True
    )

    assert (
        testing.is_testing
        is True
    )


def test_runtime_identity():

    config = PlatformConfig(
        environment="testing",
        app_name="CDCS-EMP",
        app_version="1.2.0",
    )

    runtime = RuntimeContext(
        config=config,
        runtime_id="runtime-test-001",
    )

    identity = runtime.identity()

    assert (
        identity["application_name"]
        == "CDCS-EMP"
    )

    assert (
        identity["application_version"]
        == "1.2.0"
    )

    assert (
        identity["environment"]
        == "testing"
    )

    assert (
        identity["runtime_id"]
        == "runtime-test-001"
    )


def test_runtime_validation():

    config = PlatformConfig()

    runtime = RuntimeContext(
        config=config
    )

    assert (
        runtime.validate()
        is True
    )


def test_runtime_representation():

    runtime = RuntimeContext(
        config=PlatformConfig()
    )

    representation = repr(
        runtime
    )

    assert (
        "RuntimeContext"
        in representation
    )

    assert (
        "application="
        in representation
    )

    assert (
        "environment="
        in representation
    )


def test_runtime_context_uses_configuration():

    config = PlatformConfig(
        environment="production",
        debug=True,
        testing=False,
        app_name="Enterprise Platform",
        app_version="2.5.0",
    )

    runtime = RuntimeContext(
        config=config
    )

    assert (
        runtime.application_name
        == config.app_name
    )

    assert (
        runtime.application_version
        == config.app_version
    )

    assert (
        runtime.environment
        == config.environment
    )

    assert (
        runtime.debug
        == config.debug
    )
