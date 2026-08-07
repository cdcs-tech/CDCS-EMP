"""
CDCS Enterprise Management Platform (CDCS-EMP)

Notification Framework Tests

Notification Audit Integration.
"""

from app.core.notifications.audit import (
    NotificationAuditService,
)

from app.core.notifications.base import (
    BaseNotification,
)

from app.core.security.audit import (
    SecurityAuditEvent,
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


def create_notification():
    """
    Create a test notification.
    """

    return TestNotification(
        recipient="user-001",
        title="Test Notification",
        message="Audit integration test.",
    )


def test_notification_audit_service_creation():

    registry = AuditRegistry()

    service = NotificationAuditService(
        registry=registry
    )

    assert service.registry is registry


def test_record_notification_creation():

    registry = AuditRegistry()

    service = NotificationAuditService(
        registry=registry
    )

    notification = (
        create_notification()
    )

    event = service.record_creation(
        notification
    )

    assert isinstance(
        event,
        SecurityAuditEvent,
    )

    assert (
        event.event_type
        == "NOTIFICATION_CREATED"
    )

    assert (
        event.subject
        == "user-001"
    )

    assert (
        event.resource
        == notification.notification_id
    )

    assert (
        event.action
        == "CREATE_NOTIFICATION"
    )

    assert event.result == "SUCCESS"

    assert (
        event.metadata[
            "notification_type"
        ]
        == "TEST_NOTIFICATION"
    )

    assert (
        registry.count()
        == 1
    )


def test_record_notification_delivery():

    registry = AuditRegistry()

    service = NotificationAuditService(
        registry=registry
    )

    notification = (
        create_notification()
    )

    result = {
        "status": "DELIVERED",
        "provider": "in_app",
    }

    event = service.record_delivery(
        notification=notification,
        provider_name="in_app",
        result=result,
    )

    assert isinstance(
        event,
        SecurityAuditEvent,
    )

    assert (
        event.event_type
        == "NOTIFICATION_DELIVERY"
    )

    assert (
        event.subject
        == "user-001"
    )

    assert (
        event.resource
        == notification.notification_id
    )

    assert (
        event.action
        == "SEND_NOTIFICATION"
    )

    assert event.result == "DELIVERED"

    assert (
        event.metadata[
            "provider"
        ]
        == "in_app"
    )

    assert (
        event.metadata[
            "notification_id"
        ]
        == notification.notification_id
    )

    assert (
        registry.count()
        == 1
    )


def test_notification_audit_registry_integration():

    registry = AuditRegistry()

    service = NotificationAuditService(
        registry=registry
    )

    notification = (
        create_notification()
    )

    service.record_creation(
        notification
    )

    service.record_delivery(
        notification=notification,
        provider_name="in_app",
        result={
            "status": "DELIVERED",
        },
    )

    assert (
        registry.count()
        == 2
    )

    events = registry.all()

    assert (
        events[0].event_type
        == "NOTIFICATION_CREATED"
    )

    assert (
        events[1].event_type
        == "NOTIFICATION_DELIVERY"
    )

