"""
CDCS Enterprise Management Platform (CDCS-EMP)

Notification Framework Tests

In-App Notification Provider
Integration and End-to-End Tests.
"""

from app.core.notifications.base import (
    BaseNotification,
)

from app.core.notifications.registry import (
    NotificationRegistry,
)

from app.core.notifications.service import (
    NotificationService,
)

from app.core.notifications.providers.base import (
    BaseNotificationProvider,
)

from app.core.notifications.providers.registry import (
    NotificationProviderRegistry,
)

from app.core.notifications.providers.in_app import (
    InAppNotificationProvider,
)


class TestNotification(
    BaseNotification
):
    """
    Test notification implementation.
    """

    @property
    def notification_type(self):
        return "TEST_NOTIFICATION"


def test_in_app_provider_contract():

    provider = (
        InAppNotificationProvider()
    )

    assert isinstance(
        provider,
        BaseNotificationProvider,
    )

    assert (
        provider.provider_name
        == "in_app"
    )


def test_notification_registration():

    registry = NotificationRegistry()

    registry.register(
        TestNotification
    )

    assert registry.has(
        "TEST_NOTIFICATION"
    )

    assert (
        registry.get(
            "TEST_NOTIFICATION"
        )
        is TestNotification
    )


def test_provider_registration():

    registry = (
        NotificationProviderRegistry()
    )

    provider = (
        InAppNotificationProvider()
    )

    registry.register(
        provider
    )

    assert registry.has(
        "in_app"
    )

    assert (
        registry.get(
            "in_app"
        )
        is provider
    )


def test_in_app_delivery():

    notification_registry = (
        NotificationRegistry()
    )

    provider_registry = (
        NotificationProviderRegistry()
    )

    provider = (
        InAppNotificationProvider()
    )


    notification_registry.register(
        TestNotification
    )

    provider_registry.register(
        provider
    )


    service = NotificationService(
        notification_registry_instance=(
            notification_registry
        ),
        provider_registry_instance=(
            provider_registry
        ),
    )


    result = service.notify(
        notification_type=(
            "TEST_NOTIFICATION"
        ),
        recipient="user-001",
        title="Test Notification",
        message=(
            "This is an end-to-end "
            "notification test."
        ),
        provider_name="in_app",
    )


    assert result["status"] == "DELIVERED"

    assert (
        result["provider"]
        == "in_app"
    )

    assert (
        result["recipient"]
        == "user-001"
    )

    assert (
        result["title"]
        == "Test Notification"
    )

    assert (
        provider.delivery_count()
        == 1
    )


def test_notification_service_creation_without_delivery():

    notification_registry = (
        NotificationRegistry()
    )

    provider_registry = (
        NotificationProviderRegistry()
    )


    notification_registry.register(
        TestNotification
    )


    service = NotificationService(
        notification_registry_instance=(
            notification_registry
        ),
        provider_registry_instance=(
            provider_registry
        ),
    )


    notification = service.notify(
        notification_type=(
            "TEST_NOTIFICATION"
        ),
        recipient="user-002",
        title="Deferred Notification",
        message=(
            "This notification has "
            "not been delivered yet."
        ),
    )


    assert isinstance(
        notification,
        TestNotification,
    )

    assert (
        notification.recipient
        == "user-002"
    )

    assert (
        notification.title
        == "Deferred Notification"
    )

