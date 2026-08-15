"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration resolution tests.
"""

from app.core.configuration import (
    ConfigurationResolutionContext,
    DefaultConfigurationResolver,
    ConfigurationScope,
)


def test_platform_value_is_resolved():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
    }

    context = ConfigurationResolutionContext()

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "SSP"
    )


def test_module_overrides_platform():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "USD"
    )


def test_organization_overrides_module():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
        ConfigurationScope.ORGANIZATION: {
            "currency": "EUR",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
    )

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "EUR"
    )


def test_user_overrides_organization():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
        ConfigurationScope.ORGANIZATION: {
            "currency": "EUR",
        },
        ConfigurationScope.USER: {
            "currency": "GBP",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
        user_id="user-001",
    )

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "GBP"
    )


def test_missing_specific_scope_falls_back():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "tax_enabled": True,
        },
        ConfigurationScope.ORGANIZATION: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
    )

    assert (
        resolver.resolve(
            values,
            "tax_enabled",
            context,
        )
        is True
    )


def test_missing_value_returns_default():

    resolver = DefaultConfigurationResolver()

    context = ConfigurationResolutionContext()

    assert (
        resolver.resolve(
            {},
            "currency",
            context,
            default="SSP",
        )
        == "SSP"
    )


def test_module_scope_requires_module_context():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext()

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "SSP"
    )


def test_organization_scope_requires_organization_context():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.ORGANIZATION: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "SSP"
    )


def test_user_scope_requires_user_context():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.USER: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
    )

    assert (
        resolver.resolve(
            values,
            "currency",
            context,
        )
        == "SSP"
    )


def test_equal_values_are_deterministic():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    first = resolver.resolve(
        values,
        "currency",
        context,
    )

    second = resolver.resolve(
        values,
        "currency",
        context,
    )

    assert first == second


def test_resolve_all_returns_merged_configuration():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
            "timezone": "Africa/Juba",
        },
        ConfigurationScope.MODULE: {
            "tax_enabled": True,
        },
        ConfigurationScope.ORGANIZATION: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
        organization_id="org-001",
    )

    resolved = resolver.resolve_all(
        values,
        context,
    )

    assert (
        resolved["currency"]
        == "USD"
    )

    assert (
        resolved["timezone"]
        == "Africa/Juba"
    )

    assert (
        resolved["tax_enabled"]
        is True
    )


def test_resolution_does_not_mutate_source_values():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    resolver.resolve(
        values,
        "currency",
        context,
    )

    assert (
        values[
            ConfigurationScope.PLATFORM
        ]["currency"]
        == "SSP"
    )

    assert (
        values[
            ConfigurationScope.MODULE
        ]["currency"]
        == "USD"
    )


def test_resolve_all_does_not_mutate_source_values():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "currency": "SSP",
        },
        ConfigurationScope.MODULE: {
            "currency": "USD",
        },
    }

    context = ConfigurationResolutionContext(
        module_code="finance",
    )

    resolver.resolve_all(
        values,
        context,
    )

    assert (
        values[
            ConfigurationScope.PLATFORM
        ]["currency"]
        == "SSP"
    )

    assert (
        values[
            ConfigurationScope.MODULE
        ]["currency"]
        == "USD"
    )


def test_user_scope_can_resolve_without_module_scope():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "language": "en",
        },
        ConfigurationScope.USER: {
            "language": "fr",
        },
    }

    context = ConfigurationResolutionContext(
        user_id="user-001",
    )

    assert (
        resolver.resolve(
            values,
            "language",
            context,
        )
        == "fr"
    )


def test_organization_scope_can_resolve_without_module_scope():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "timezone": "UTC",
        },
        ConfigurationScope.ORGANIZATION: {
            "timezone": "Africa/Juba",
        },
    }

    context = ConfigurationResolutionContext(
        organization_id="org-001",
    )

    assert (
        resolver.resolve(
            values,
            "timezone",
            context,
        )
        == "Africa/Juba"
    )


def test_platform_is_always_available():

    resolver = DefaultConfigurationResolver()

    values = {
        ConfigurationScope.PLATFORM: {
            "language": "en",
        },
    }

    context = ConfigurationResolutionContext()

    assert (
        resolver.resolve(
            values,
            "language",
            context,
        )
        == "en"
    )
