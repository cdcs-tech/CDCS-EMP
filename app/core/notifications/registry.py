"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Notification Registry

Maintains registered notification types.
"""

from app.core.notifications.base import (
    BaseNotification,
)

from app.core.notifications.exceptions import (
    NotificationRegistrationException,
)


class NotificationRegistry:
    """
    Central registry for enterprise
    notification types.
    """

    def __init__(self):
        """
        Initialize notification registry.
        """

        self._notifications = {}


    def _get_notification_type(
        self,
        notification_class,
    ):
        """
        Resolve the notification type from
        a notification class.

        Notification types are currently
        exposed through the BaseNotification
        instance property. An uninitialized
        instance is used here so registration
        does not require notification
        construction arguments.
        """

        try:

            notification = object.__new__(
                notification_class
            )

            notification_type = (
                notification.notification_type
            )

        except Exception as exc:

            raise NotificationRegistrationException(
                "Invalid notification definition."
            ) from exc


        if not isinstance(
            notification_type,
            str,
        ):

            raise NotificationRegistrationException(
                "Notification type must be a string."
            )


        notification_type = (
            notification_type.strip()
        )


        if not notification_type:

            raise NotificationRegistrationException(
                "Notification type is required."
            )


        return notification_type


    def register(
        self,
        notification_class,
    ):
        """
        Register a notification type.

        The notification class must inherit
        from BaseNotification.
        """

        if not isinstance(
            notification_class,
            type,
        ):

            raise NotificationRegistrationException(
                "Notification must be a class."
            )


        if not issubclass(
            notification_class,
            BaseNotification,
        ):

            raise NotificationRegistrationException(
                "Notification must inherit "
                "from BaseNotification."
            )


        notification_type = (
            self._get_notification_type(
                notification_class
            )
        )


        self._notifications[
            notification_type
        ] = notification_class


    def get(
        self,
        notification_type,
    ):
        """
        Retrieve a registered notification
        class.
        """

        return self._notifications.get(
            notification_type
        )


    def has(
        self,
        notification_type,
    ):
        """
        Determine whether a notification
        type is registered.
        """

        return (
            notification_type
            in self._notifications
        )


    def all(self):
        """
        Return all registered notification
        classes.
        """

        return dict(
            self._notifications
        )


    def count(self):
        """
        Return the number of registered
        notification types.
        """

        return len(
            self._notifications
        )


    def clear(self):
        """
        Clear the registry.

        Primarily intended for testing.
        """

        self._notifications.clear()


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<NotificationRegistry "
            f"notifications="
            f"{self.count()}>"
        )


notification_registry = (
    NotificationRegistry()
)

