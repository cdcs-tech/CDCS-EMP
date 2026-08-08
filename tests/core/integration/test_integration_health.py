"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration health service tests.
"""

import pytest

from app.core.integration import (
    IntegrationHealthResult,
    IntegrationHealthService,
)

from app.core.integration.providers import (
    BaseIntegrationProvider,
    IntegrationProviderRegistry,
)


class HealthyProvider(
    BaseIntegrationProvider
):
    """
    Provider that reports healthy.
    """

    @property
    def provider_name(self):
        return "healthy_provider"


    def execute(
        self,
        request,
    ):
        return None


    def health_check(
        self,
    ):
        return True


class UnhealthyProvider(
    BaseIntegrationProvider
):
    """
    Provider that reports unhealthy.
    """

    @property
    def provider_name(self):
        return "unhealthy_provider"


    def execute(
        self,
        request,
    ):
        return None


    def health_check(
        self,
    ):
        return False


class FailingHealthProvider(
    BaseIntegrationProvider
):
    """
    Provider whose health check raises
    an exception.
    """

    @property
    def provider_name(self):
        return "failing_health_provider"


    def execute(
        self,
        request,
    ):
        return None


    def health_check(
        self,
    ):
        raise RuntimeError(
            "Connectivity failure."
        )


def create_service():

    registry = (
        IntegrationProviderRegistry()
    )

    registry.register(
        HealthyProvider()
    )

    registry.register(
        UnhealthyProvider()
    )

    registry.register(
        FailingHealthProvider()
    )

    return IntegrationHealthService(
        provider_registry=registry
    )


def test_health_result_healthy():

    result = IntegrationHealthResult(
        provider="test_provider",
        healthy=True,
        message="Provider is healthy.",
    )

    assert result.healthy is True

    assert (
        result.status
        == "HEALTHY"
    )

    assert result.checked_at is not None


def test_health_result_unhealthy():

    result = IntegrationHealthResult(
        provider="test_provider",
        healthy=False,
        message="Provider is unhealthy.",
    )

    assert result.healthy is False

    assert (
        result.status
        == "UNHEALTHY"
    )


def test_check_healthy_provider():

    service = create_service()

    result = service.check(
        "healthy_provider"
    )

    assert isinstance(
        result,
        IntegrationHealthResult,
    )

    assert result.healthy is True

    assert (
        result.status
        == "HEALTHY"
    )


def test_check_unhealthy_provider():

    service = create_service()

    result = service.check(
        "unhealthy_provider"
    )

    assert result.healthy is False

    assert (
        result.status
        == "UNHEALTHY"
    )


def test_check_failing_health_provider():

    service = create_service()

    result = service.check(
        "failing_health_provider"
    )

    assert result.healthy is False

    assert (
        result.status
        == "UNHEALTHY"
    )

    assert (
        result.metadata["exception"]
        == "RuntimeError"
    )


def test_check_missing_provider():

    service = create_service()

    result = service.check(
        "missing_provider"
    )

    assert result.healthy is False

    assert (
        "not registered"
        in result.message
    )


def test_check_all():

    service = create_service()

    results = service.check_all()

    assert len(
        results
    ) == 3

    provider_names = {
        result.provider
        for result in results
    }

    assert provider_names == {
        "healthy_provider",
        "unhealthy_provider",
        "failing_health_provider",
    }


def test_healthy_method():

    service = create_service()

    assert (
        service.healthy(
            "healthy_provider"
        )
        is True
    )

    assert (
        service.healthy(
            "unhealthy_provider"
        )
        is False
    )


def test_healthy_count():

    service = create_service()

    assert (
        service.healthy_count()
        == 1
    )


def test_unhealthy_count():

    service = create_service()

    assert (
        service.unhealthy_count()
        == 2
    )


def test_health_service_repr():

    service = create_service()

    representation = repr(
        service
    )

    assert (
        "IntegrationHealthService"
        in representation
    )

    assert (
        "providers=3"
        in representation
    )

