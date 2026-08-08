"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework

Integration Exceptions

Defines the standard exception hierarchy
for enterprise integrations.
"""


class IntegrationException(Exception):
    """
    Base exception for all enterprise
    integration errors.
    """

    pass


class IntegrationConfigurationException(
    IntegrationException
):
    """
    Raised when an integration is incorrectly
    configured.
    """

    pass


class IntegrationRegistrationException(
    IntegrationException
):
    """
    Raised when an integration provider or
    integration definition cannot be registered.
    """

    pass


class IntegrationConnectionException(
    IntegrationException
):
    """
    Raised when a connection to an external
    or internal integration target fails.
    """

    pass


class IntegrationAuthenticationException(
    IntegrationConnectionException
):
    """
    Raised when authentication with an
    integration target fails.
    """

    pass


class IntegrationTimeoutException(
    IntegrationConnectionException
):
    """
    Raised when an integration operation
    exceeds its configured timeout.
    """

    pass


class IntegrationRequestException(
    IntegrationException
):
    """
    Raised when an integration request is
    invalid or cannot be processed.
    """

    pass


class IntegrationResponseException(
    IntegrationException
):
    """
    Raised when an integration target returns
    an invalid or unexpected response.
    """

    pass


class IntegrationDeliveryException(
    IntegrationException
):
    """
    Raised when an integration operation
    cannot successfully deliver its request.
    """

    pass


class IntegrationHealthException(
    IntegrationException
):
    """
    Raised when an integration provider fails
    a health or connectivity check.
    """

    pass


class IntegrationGovernanceException(
    IntegrationException
):
    """
    Raised when an integration operation
    violates an enterprise governance rule.
    """

    pass

