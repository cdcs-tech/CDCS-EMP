"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration request/response model tests.
"""

from datetime import datetime, timezone

import pytest

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
)


def test_integration_request_creation():

    request = IntegrationRequest(
        provider="test_provider",
        operation="create",
        payload={
            "name": "Test"
        },
    )

    assert (
        request.provider
        == "test_provider"
    )

    assert (
        request.operation
        == "create"
    )

    assert request.payload == {
        "name": "Test"
    }

    assert request.request_id

    assert isinstance(
        request.created_at,
        datetime,
    )

    assert (
        request.created_at.tzinfo
        == timezone.utc
    )


def test_integration_request_requires_provider():

    with pytest.raises(
        ValueError,
        match="provider is required",
    ):

        IntegrationRequest(
            provider="",
            operation="create",
        )


def test_integration_request_requires_operation():

    with pytest.raises(
        ValueError,
        match="operation is required",
    ):

        IntegrationRequest(
            provider="test_provider",
            operation="",
        )


def test_integration_request_rejects_invalid_timeout():

    with pytest.raises(
        ValueError,
        match="timeout must be greater than zero",
    ):

        IntegrationRequest(
            provider="test_provider",
            operation="create",
            timeout=0,
        )


def test_integration_response_success():

    response = IntegrationResponse(
        success=True,
        status_code=200,
        data={
            "id": 100
        },
        message="Operation successful.",
    )

    assert response.success is True
    assert response.failed is False
    assert response.status_code == 200
    assert response.data == {
        "id": 100
    }


def test_integration_response_failure():

    response = IntegrationResponse(
        success=False,
        status_code=500,
        error="Remote service failed.",
    )

    assert response.success is False
    assert response.failed is True
    assert (
        response.error
        == "Remote service failed."
    )


def test_integration_result_success():

    request = IntegrationRequest(
        provider="test_provider",
        operation="create",
    )

    response = IntegrationResponse(
        success=True,
        status_code=200,
    )

    result = IntegrationResult(
        request=request,
        response=response,
        duration_ms=125.5,
    )

    assert result.success is True
    assert result.failed is False
    assert (
        result.provider is None
    )


def test_integration_result_failure():

    request = IntegrationRequest(
        provider="test_provider",
        operation="create",
    )

    response = IntegrationResponse(
        success=False,
        status_code=500,
        error="Remote service failed.",
    )

    result = IntegrationResult(
        request=request,
        response=response,
    )

    assert result.success is False
    assert result.failed is True


def test_integration_result_without_response():

    request = IntegrationRequest(
        provider="test_provider",
        operation="create",
    )

    result = IntegrationResult(
        request=request
    )

    assert result.success is False
    assert result.failed is True

