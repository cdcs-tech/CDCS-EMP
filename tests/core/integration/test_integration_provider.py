"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration provider contract tests.
"""

import pytest

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)

from app.core.integration.providers import (
    BaseIntegrationProvider,
)


class TestIntegrationProvider(
    BaseIntegrationProvider
):
    """
    Concrete provider used to verify the
    base integration provider contract.
    """

    @property
    def provider_name(self):
        return "test_provider"


    def execute(
        self,
        request,
    ):
        return IntegrationResponse(
            success=True,
            status_code=200,
            data={
                "status": "ok"
            },
            request_id=request.request_id,
        )


def test_provider_name():

    provider = TestIntegrationProvider()

    assert (
        provider.provider_name
        == "test_provider"
    )


def test_provider_version():

    provider = TestIntegrationProvider()

    assert (
        provider.provider_version
        == "1.0.0"
    )


def test_provider_execute():

    provider = TestIntegrationProvider()

    request = IntegrationRequest(
        provider="test_provider",
        operation="health",
    )

    response = provider.execute(
        request
    )

    assert isinstance(
        response,
        IntegrationResponse,
    )

    assert response.success is True

    assert (
        response.request_id
        == request.request_id
    )


def test_provider_validation():

    provider = TestIntegrationProvider()

    request = IntegrationRequest(
        provider="test_provider",
        operation="test",
    )

    assert (
        provider.validate(request)
        is None
    )


def test_provider_rejects_invalid_request():

    provider = TestIntegrationProvider()

    with pytest.raises(
        TypeError,
        match="Integration request",
    ):

        provider.validate(
            "invalid request"
        )


def test_provider_supports_operation():

    provider = TestIntegrationProvider()

    assert (
        provider.supports("test")
        is True
    )


def test_provider_health_check():

    provider = TestIntegrationProvider()

    assert (
        provider.health_check()
        is True
    )


def test_provider_close():

    provider = TestIntegrationProvider()

    assert (
        provider.close()
        is None
    )


def test_provider_representation():

    provider = TestIntegrationProvider()

    representation = repr(
        provider
    )

    assert (
        "test_provider"
        in representation
    )

    assert (
        "1.0.0"
        in representation
    )

