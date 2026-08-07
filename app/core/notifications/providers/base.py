"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Notification Framework

Base Notification Provider

Defines the standard contract that all
notification delivery providers must follow.
"""

from abc import ABC, abstractmethod

from app.core.notifications.base import (
    BaseNotification,
)


class BaseNotificationProvider(ABC):
    """
    Abstract base class for notification
    delivery providers.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the unique provider name.
        """

        raise NotImplementedError


    @abstractmethod
    def supports(
        self,
        notification: BaseNotification,
    ) -> bool:
        """
        Determine whether this provider
        supports the supplied notification.
        """

        raise NotImplementedError


    @abstractmethod
    def send(
        self,
        notification: BaseNotification,
    ):
        """
        Deliver a notification.

        Implementations must return a
        provider-specific delivery result.
        """

        raise NotImplementedError


    def validate(
        self,
        notification: BaseNotification,
    ) -> bool:
        """
        Validate a notification before delivery.
        """

        if not isinstance(
            notification,
            BaseNotification,
        ):
            raise TypeError(
                "Provider can only process "
                "BaseNotification instances."
            )

        notification.validate()

        return True


    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<NotificationProvider "
            f"{self.provider_name}>"
        )

