"""
CDCS Enterprise Management Platform (CDCS-EMP)

Notification Framework Tests

Notification Failure & Governance Handling.
"""

import pytest

from app.core.notifications.base import (
    BaseNotification,
)

from app.core.notifications.exceptions import (
    NotificationDeliveryException,
    NotificationRegistrationException,
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

from app.core.notifications.audit import (
    NotificationAuditService,
)

from app.core.security.audit_registry import (
    AuditRegistry,
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


class FailingNotificationProvider(
    BaseNotificationProvider
):
    """
    Provider that deliberately fails during
    notification delivery.

    Used to verify failure handling and
    governance behavior.
    """

    @property
    def provider_name(self):
        return "failing_provider"


    def supports(
        self,
        notification,
    ):
        return isinstance(
            notification,
            BaseNotification,
        )


    def send(
        self,
        notification,
    ):
        raise RuntimeError(
            "Simulated provider failure."
        )


def build_service():
    """
    Build an isolated notification service
    with isolated notification, provider,
    and audit registries.
    """

    notification_registry = (
        NotificationRegistry()
    )

    provider_registry = (
        NotificationProviderRegistry()
    )

    audit_registry = AuditRegistry()

    audit_service = (
        NotificationAuditService(
            registry=audit_registry
        )
    )

    notification_registry.register(
        TestNotification
    )

    provider = (
        FailingNotificationProvider()
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
        audit_service=audit_service,
    )

    return (
        service,
        audit_registry,
    )


def test_unregistered_notification_type_fails():

    service, audit_registry = (
        build_service()
    )

    with pytest.raises(
        NotificationRegistrationException
    ):

        service.notify(
            notification_type=(
                "UNKNOWN_NOTIFICATION"
            ),
            recipient="user-001",
            title="Test",
            message="Test",
        )

    assert (
        audit_registry.count()
        == 0
    )


def test_unregistered_provider_fails():

    service, audit_registry = (
        build_service()
    )

    with pytest.raises(
        NotificationDeliveryException
    ):

        service.notify(
            notification_type=(
                "TEST_NOTIFICATION"
            ),
            recipient="user-001",
            title="Test",
            message="Test",
            provider_name="unknown_provider",
        )

    assert (
        audit_registry.count()
        == 1
    )

    assert (
        audit_registry.latest().event_type
        == "NOTIFICATION_CREATED"
    )


def test_provider_failure_is_wrapped():

    service, audit_registry = (
        build_service()
    )

    with pytest.raises(
        NotificationDeliveryException
    ) as exc_info:

        service.notify(
            notification_type=(
                "TEST_NOTIFICATION"
            ),
            recipient="user-001",
            title="Test",
            message="Test",
            provider_name="failing_provider",
        )

    assert (
        "Notification delivery failed."
        in str(exc_info.value)
    )

    assert isinstance(
        exc_info.value.__cause__,
        RuntimeError,
    )


def test_provider_failure_is_audited():

    service, audit_registry = (
        build_service()
    )

    with pytest.raises(
        NotificationDeliveryException
    ):

        service.notify(
            notification_type=(
                "TEST_NOTIFICATION"
            ),
            recipient="user-001",
            title="Test",
            message="Test",
            provider_name="failing_provider",
        )

    events = (
        audit_registry.all()
    )

    assert (
        len(events)
        == 2
    )

    assert (
        events[0].event_type
        == "NOTIFICATION_CREATED"
    )

    assert (
        events[1].event_type
        == "NOTIFICATION_DELIVERY"
    )

    assert (
        events[1].result
        == "FAILED"
    )

    assert (
        events[1].metadata[
            "provider"
        ]
        == "failing_provider"
    )


def test_successful_delivery_is_not_marked_failed():

    service, audit_registry = (
        build_service()
    )

    class SuccessfulProvider(
        BaseNotificationProvider
    ):
        @property
        def provider_name(self):
            return "successful_provider"

        def supports(
            self,
            notification,
        ):
            return True

        def send(
            self,
            notification,
        ):
            return {
                "status": "DELIVERED",
                "provider": (
                    "successful_provider"
                ),
            }

    provider_registry = (
        service.provider_registry
    )

    provider_registry.register(
        SuccessfulProvider()
    )

    result = service.notify(
        notification_type=(
            "TEST_NOTIFICATION"
        ),
        recipient="user-001",
        title="Test",
        message="Test",
        provider_name="successful_provider",
    )

    assert (
        result["status"]
        == "DELIVERED"
    )

    delivery_event = (
        audit_registry.latest()
    )

    assert (
        delivery_event.event_type
        == "NOTIFICATION_DELIVERY"
    )

    assert (
        delivery_event.result
        == "DELIVERED"
    )

