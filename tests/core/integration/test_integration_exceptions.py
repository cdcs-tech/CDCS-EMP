"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration exception hierarchy tests.
"""

import pytest

from app.core.integration import (
    IntegrationException,
    IntegrationConfigurationException,
    IntegrationRegistrationException,
    IntegrationConnectionException,
    IntegrationAuthenticationException,
    IntegrationTimeoutException,
    IntegrationRequestException,
    IntegrationResponseException,
    IntegrationDeliveryException,
    IntegrationHealthException,
    IntegrationGovernanceException,
)


def test_all_exceptions_inherit_from_integration_exception():

    exception_classes = [
        IntegrationConfigurationException,
        IntegrationRegistrationException,
        IntegrationConnectionException,
        IntegrationAuthenticationException,
        IntegrationTimeoutException,
        IntegrationRequestException,
        IntegrationResponseException,
        IntegrationDeliveryException,
        IntegrationHealthException,
        IntegrationGovernanceException,
    ]

    for exception_class in exception_classes:

        assert issubclass(
            exception_class,
            IntegrationException,
        )


def test_connection_specialized_exceptions():

    assert issubclass(
        IntegrationAuthenticationException,
        IntegrationConnectionException,
    )

    assert issubclass(
        IntegrationTimeoutException,
        IntegrationConnectionException,
    )


def test_exceptions_preserve_messages():

    message = (
        "Integration operation failed."
    )

    exception = IntegrationDeliveryException(
        message
    )

    assert str(exception) == message


def test_exceptions_can_be_raised_and_caught():

    with pytest.raises(
        IntegrationException
    ):

        raise IntegrationRequestException(
            "Invalid integration request."
        )


def test_specific_exception_can_be_caught_as_parent():

    with pytest.raises(
        IntegrationConnectionException
    ):

        raise IntegrationTimeoutException(
            "Integration request timed out."
        )

