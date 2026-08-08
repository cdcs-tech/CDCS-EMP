"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration provider registry tests.
"""

import pytest

from app.core.integration import (
    IntegrationRegistrationException,
)

from app.core.integration.providers import (
    BaseIntegrationProvider,
    IntegrationProviderRegistry,
)


class TestProvider(
    BaseIntegrationProvider
):
    """
    Test provider used for registry testing.
    """

    def __init__(
        self,
        name="test_provider",
    ):
        self._name = name


    @property
    def provider_name(self):
        return self._name


    def execute(
        self,
        request,
    ):
        return None


def test_registry_registers_provider():

    registry = (
        IntegrationProviderRegistry()
    )

    provider = TestProvider()

    registry.register(
        provider
    )

    assert (
        registry.get(
            "test_provider"
        )
        is provider
    )


def test_registry_has_provider():

    registry = (
        IntegrationProviderRegistry()
    )

    provider = TestProvider()

    registry.register(
        provider
    )

    assert (
        registry.has(
            "test_provider"
        )
        is True
    )


def test_registry_missing_provider():

    registry = (
        IntegrationProviderRegistry()
    )

    assert (
        registry.get(
            "missing_provider"
        )
        is None
    )

    assert (
        registry.has(
            "missing_provider"
        )
        is False
    )


def test_registry_rejects_invalid_provider():

    registry = (
        IntegrationProviderRegistry()
    )

    with pytest.raises(
        IntegrationRegistrationException
    ):

        registry.register(
            "invalid provider"
        )


def test_registry_rejects_duplicate_provider():

    registry = (
        IntegrationProviderRegistry()
    )

    provider = TestProvider()

    registry.register(
        provider
    )

    with pytest.raises(
        IntegrationRegistrationException,
        match="already registered",
    ):

        registry.register(
            provider
        )


def test_registry_all():

    registry = (
        IntegrationProviderRegistry()
    )

    provider_a = TestProvider(
        "provider_a"
    )

    provider_b = TestProvider(
        "provider_b"
    )

    registry.register(
        provider_a
    )

    registry.register(
        provider_b
    )

    providers = registry.all()

    assert len(
        providers
    ) == 2

    assert provider_a in providers
    assert provider_b in providers


def test_registry_names():

    registry = (
        IntegrationProviderRegistry()
    )

    registry.register(
        TestProvider("provider_a")
    )

    registry.register(
        TestProvider("provider_b")
    )

    assert (
        registry.names()
        == [
            "provider_a",
            "provider_b",
        ]
    )


def test_registry_count():

    registry = (
        IntegrationProviderRegistry()
    )

    assert (
        registry.count()
        == 0
    )

    registry.register(
        TestProvider()
    )

    assert (
        registry.count()
        == 1
    )


def test_registry_clear():

    registry = (
        IntegrationProviderRegistry()
    )

    registry.register(
        TestProvider()
    )

    registry.clear()

    assert (
        registry.count()
        == 0
    )

    assert (
        registry.has(
            "test_provider"
        )
        is False
    )


def test_registry_iteration():

    registry = (
        IntegrationProviderRegistry()
    )

    provider_a = TestProvider(
        "provider_a"
    )

    provider_b = TestProvider(
        "provider_b"
    )

    registry.register(
        provider_a
    )

    registry.register(
        provider_b
    )

    providers = list(
        registry
    )

    assert providers == [
        provider_a,
        provider_b,
    ]


def test_registry_repr():

    registry = (
        IntegrationProviderRegistry()
    )

    registry.register(
        TestProvider()
    )

    representation = repr(
        registry
    )

    assert (
        "IntegrationProviderRegistry"
        in representation
    )

    assert (
        "1 providers"
        in representation
    )

