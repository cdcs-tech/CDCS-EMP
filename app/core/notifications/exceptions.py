"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Notification Exceptions

Defines the standard exception hierarchy
for the notification framework.
"""


class NotificationException(Exception):
    """
    Base exception for notification errors.
    """

    pass


class NotificationValidationException(
    NotificationException
):
    """
    Raised when a notification fails
    contract or data validation.
    """

    pass


class NotificationRegistrationException(
    NotificationException
):
    """
    Raised when notification registration
    fails.
    """

    pass


class NotificationDeliveryException(
    NotificationException
):
    """
    Raised when notification delivery fails.
    """

    pass


class NotificationProviderException(
    NotificationException
):
    """
    Raised when a notification provider
    encounters an error.
    """

    pass

