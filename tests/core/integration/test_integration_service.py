"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration service tests.
"""

import pytest

from app.core.integration import (
    IntegrationDeliveryException,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationRequestException,
    IntegrationResult,
    IntegrationService,
)

from app.core.integration.exceptions import (
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
    Successful test integration provider.
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
                "message": "success"
            },
        )


class UnsupportedProvider(
    BaseIntegrationProvider
):
    """
    Provider that rejects the requested
    operation.
    """

    @property
    def provider_name(self):
        return "unsupported_provider"


    def execute(
        self,
        request,
    ):

        return IntegrationResponse(
            success=True
        )


    def supports(
        self,
        operation,
    ):

        return False


class FailingProvider(
    BaseIntegrationProvider
):
    """
    Provider that raises an exception
    during execution.
    """

    @property
    def provider_name(self):
        return "failing_provider"


    def execute(
        self,
        request,
    ):

        raise RuntimeError(
            "Remote service unavailable."
        )


class InvalidResponseProvider(
    BaseIntegrationProvider
):
    """
    Provider that returns an invalid
    response object.
    """

    @property
    def provider_name(self):
        return "invalid_response_provider"


    def execute(
        self,
        request,
    ):

        return "invalid response"


def create_service():

    registry = (
        IntegrationProviderRegistry()
    )

    registry.register(
        TestProvider()
    )

    registry.register(
        UnsupportedProvider()
    )

    registry.register(
        FailingProvider()
    )

    registry.register(
        InvalidResponseProvider()
    )

    return IntegrationService(
        provider_registry=registry
    )


def test_execute_successfully():

    service = create_service()

    request = IntegrationRequest(
        provider="test_provider",
        operation="create",
    )

    result = service.execute(
        request
    )

    assert isinstance(
        result,
        IntegrationResult,
    )

    assert result.success is True

    assert result.failed is False

    assert (
        result.provider
        == "test_provider"
    )

    assert (
        result.operation
        == "create"
    )

    assert (
        result.response.status_code
        == 200
    )

    assert (
        result.response.request_id
        == request.request_id
    )

    assert (
        result.duration_ms
        is not None
    )


def test_unknown_provider():

    service = create_service()

    request = IntegrationRequest(
        provider="missing_provider",
        operation="create",
    )

    with pytest.raises(
        IntegrationRegistrationException
    ):

        service.execute(
            request
        )


def test_invalid_request_type():

    service = create_service()

    with pytest.raises(
        IntegrationRequestException
    ):

        service.execute(
            "invalid request"
        )


def test_unsupported_operation():

    service = create_service()

    request = IntegrationRequest(
        provider="unsupported_provider",
        operation="delete",
    )

    with pytest.raises(
        IntegrationRequestException,
        match="does not support operation",
    ):

        service.execute(
            request
        )


def test_provider_execution_failure():

    service = create_service()

    request = IntegrationRequest(
        provider="failing_provider",
        operation="create",
    )

    with pytest.raises(
        IntegrationDeliveryException
    ) as exc_info:

        service.execute(
            request
        )

    assert isinstance(
        exc_info.value.__cause__,
        RuntimeError,
    )


def test_invalid_provider_response():

    service = create_service()

    request = IntegrationRequest(
        provider="invalid_response_provider",
        operation="create",
    )

    with pytest.raises(
        IntegrationDeliveryException,
        match="returned an invalid response",
    ):

        service.execute(
            request
        )


def test_has_provider():

    service = create_service()

    assert (
        service.has_provider(
            "test_provider"
        )
        is True
    )

    assert (
        service.has_provider(
            "missing_provider"
        )
        is False
    )


def test_provider_count():

    service = create_service()

    assert (
        service.provider_count()
        == 4
    )


def test_service_representation():

    service = create_service()

    representation = repr(
        service
    )

    assert (
        "IntegrationService"
        in representation
    )

    assert (
        "providers=4"
        in representation
    )
