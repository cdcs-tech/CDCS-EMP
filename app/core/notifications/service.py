"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Notification Service

Central orchestration service responsible for
creating, validating, delivering, and auditing
notifications.
"""

from app.core.notifications.exceptions import (
    NotificationDeliveryException,
    NotificationRegistrationException,
)

from app.core.notifications.registry import (
    notification_registry,
)

from app.core.notifications.providers.registry import (
    notification_provider_registry,
)

from app.core.notifications.audit import (
    NotificationAuditService,
    notification_audit_service,
)


class NotificationService:
    """
    Central notification orchestration service.
    """

    def __init__(
        self,
        notification_registry_instance=None,
        provider_registry_instance=None,
        audit_service=None,
    ):
        """
        Initialize notification service.
        """

        self.notification_registry = (
            notification_registry_instance
            or notification_registry
        )

        self.provider_registry = (
            provider_registry_instance
            or notification_provider_registry
        )

        self.audit_service = (
            audit_service
            or notification_audit_service
        )


    def create(
        self,
        notification_type,
        recipient,
        title="",
        message="",
        metadata=None,
    ):
        """
        Create and validate a notification.
        """

        notification_class = (
            self.notification_registry.get(
                notification_type
            )
        )

        if notification_class is None:

            raise NotificationRegistrationException(
                f"Notification type "
                f"'{notification_type}' "
                f"is not registered."
            )


        notification = notification_class(
            recipient=recipient,
            title=title,
            message=message,
            metadata=metadata,
        )


        notification.validate()


        self.audit_service.record_creation(
            notification
        )


        return notification


    def send(
        self,
        notification,
        provider_name,
    ):
        """
        Deliver a notification using the
        requested provider and record the
        delivery outcome in the audit registry.
        """

        provider = (
            self.provider_registry.get(
                provider_name
            )
        )

        if provider is None:

            raise NotificationDeliveryException(
                f"Notification provider "
                f"'{provider_name}' "
                f"is not registered."
            )


        if not provider.supports(
            notification
        ):

            raise NotificationDeliveryException(
                f"Provider "
                f"'{provider_name}' "
                f"does not support notification "
                f"'{notification.notification_type}'."
            )


        try:

            provider.validate(
                notification
            )

            result = provider.send(
                notification
            )


            self.audit_service.record_delivery(
                notification=notification,
                provider_name=provider_name,
                result=result,
            )


            return result


        except NotificationDeliveryException:

            raise


        except Exception as exc:

            failure_result = {
                "status": "FAILED",
                "provider": provider_name,
                "error": str(exc),
            }


            try:

                self.audit_service.record_delivery(
                    notification=notification,
                    provider_name=provider_name,
                    result=failure_result,
                )

            except Exception:
                # Audit failure must not hide the
                # original notification failure.
                pass


            raise NotificationDeliveryException(
                "Notification delivery failed."
            ) from exc


    def notify(
        self,
        notification_type,
        recipient,
        title="",
        message="",
        metadata=None,
        provider_name=None,
    ):
        """
        Create and optionally deliver a
        notification.

        When provider_name is supplied,
        the notification is immediately
        delivered.

        Otherwise, the validated notification
        instance is returned for later delivery.
        """

        notification = self.create(
            notification_type=notification_type,
            recipient=recipient,
            title=title,
            message=message,
            metadata=metadata,
        )


        if provider_name is None:

            return notification


        return self.send(
            notification,
            provider_name,
        )


    def has_notification_type(
        self,
        notification_type,
    ):
        """
        Determine whether a notification type
        is registered.
        """

        return self.notification_registry.has(
            notification_type
        )


    def has_provider(
        self,
        provider_name,
    ):
        """
        Determine whether a provider is
        registered.
        """

        return self.provider_registry.has(
            provider_name
        )


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<NotificationService "
            f"notifications="
            f"{self.notification_registry.count()} "
            f"providers="
            f"{self.provider_registry.count()}>"
        )


notification_service = NotificationService()

