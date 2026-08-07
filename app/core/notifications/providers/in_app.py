"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

In-App Notification Provider

Provides the initial notification delivery
mechanism for notifications displayed
inside the CDCS-EMP application.
"""

from app.core.notifications.base import (
    BaseNotification,
)

from app.core.notifications.providers.base import (
    BaseNotificationProvider,
)


class InAppNotificationProvider(
    BaseNotificationProvider
):
    """
    In-App notification delivery provider.

    This initial implementation keeps delivery
    in memory. Persistent storage will be added
    in a later stage.
    """

    def __init__(self):
        """
        Initialize the provider.
        """

        self._deliveries = []


    @property
    def provider_name(self) -> str:
        """
        Return the unique provider name.
        """

        return "in_app"


    def supports(
        self,
        notification: BaseNotification,
    ) -> bool:
        """
        Determine whether the provider supports
        the supplied notification.
        """

        return isinstance(
            notification,
            BaseNotification,
        )


    def send(
        self,
        notification: BaseNotification,
    ):
        """
        Deliver notification in memory.

        Returns a standardized delivery result.
        """

        self.validate(
            notification
        )


        delivery = {
            "notification_id": (
                notification.notification_id
            ),
            "notification_type": (
                notification.notification_type
            ),
            "recipient": (
                notification.recipient
            ),
            "title": (
                notification.title
            ),
            "message": (
                notification.message
            ),
            "status": "DELIVERED",
            "provider": (
                self.provider_name
            ),
            "created_at": (
                notification.created_at
            ),
        }


        self._deliveries.append(
            delivery
        )


        return delivery


    def deliveries(self):
        """
        Return all in-memory deliveries.
        """

        return list(
            self._deliveries
        )


    def delivery_count(self) -> int:
        """
        Return the number of deliveries.
        """

        return len(
            self._deliveries
        )


    def clear(self):
        """
        Clear in-memory deliveries.

        Primarily intended for testing.
        """

        self._deliveries.clear()


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<InAppNotificationProvider "
            f"deliveries="
            f"{self.delivery_count()}>"
        )


in_app_provider = (
    InAppNotificationProvider()
)

