"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Notification Audit Integration

Provides standardized audit integration for
notification creation and delivery activities.
"""

from app.core.security.audit import (
    SecurityAuditEvent,
)

from app.core.security.audit_registry import (
    audit_registry,
)


class NotificationAuditService:
    """
    Service responsible for recording
    notification-related audit events.
    """

    def __init__(
        self,
        registry=None,
    ):
        """
        Initialize notification audit service.
        """

        self.registry = (
            registry
            or audit_registry
        )


    def record_delivery(
        self,
        notification,
        provider_name,
        result,
    ):
        """
        Record a notification delivery
        audit event.
        """

        status = (
            result.get(
                "status",
                "SUCCESS",
            )
            if isinstance(
                result,
                dict,
            )
            else "SUCCESS"
        )


        audit_event = SecurityAuditEvent(
            event_type=(
                "NOTIFICATION_DELIVERY"
            ),
            subject=str(
                notification.recipient
            ),
            resource=(
                notification.notification_id
            ),
            action=(
                "SEND_NOTIFICATION"
            ),
            result=status,
            message=(
                f"Notification "
                f"'{notification.notification_type}' "
                f"delivered using "
                f"provider "
                f"'{provider_name}'."
            ),
            metadata={
                "notification_id": (
                    notification.notification_id
                ),
                "notification_type": (
                    notification.notification_type
                ),
                "provider": (
                    provider_name
                ),
                "recipient": (
                    notification.recipient
                ),
            },
        )


        self.registry.record(
            audit_event
        )


        return audit_event


    def record_creation(
        self,
        notification,
    ):
        """
        Record notification creation
        as an audit event.
        """

        audit_event = SecurityAuditEvent(
            event_type=(
                "NOTIFICATION_CREATED"
            ),
            subject=str(
                notification.recipient
            ),
            resource=(
                notification.notification_id
            ),
            action=(
                "CREATE_NOTIFICATION"
            ),
            result="SUCCESS",
            message=(
                f"Notification "
                f"'{notification.notification_type}' "
                f"created."
            ),
            metadata={
                "notification_id": (
                    notification.notification_id
                ),
                "notification_type": (
                    notification.notification_type
                ),
                "recipient": (
                    notification.recipient
                ),
            },
        )


        self.registry.record(
            audit_event
        )


        return audit_event


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<NotificationAuditService "
            f"registry={self.registry}>"
        )


notification_audit_service = (
    NotificationAuditService()
)

